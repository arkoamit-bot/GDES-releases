"""Cross-disease knowledge graph: population, traversal, and reasoning services."""
import logging
from collections import deque

from django.db import models as db_models
from django.db import transaction

from .models import (
    KnowledgeGraphNode, KnowledgeGraphEdge,
    Syndrome, PathologyEntity, LabEntity, DrugIntelligence,
    MonitoringProtocol, Complication, Disease,
)

logger = logging.getLogger(__name__)


# ─── Graph Population ─────────────────────────────────────────────────────


NODE_TYPE_MAP = {
    "syndrome": KnowledgeGraphNode.NodeType.SYNDROME,
    "disease": KnowledgeGraphNode.NodeType.DISEASE,
    "pathology": KnowledgeGraphNode.NodeType.PATHOLOGY,
    "lab": KnowledgeGraphNode.NodeType.LAB,
    "drug": KnowledgeGraphNode.NodeType.DRUG,
    "monitoring_protocol": KnowledgeGraphNode.NodeType.MONITORING,
    "complication": KnowledgeGraphNode.NodeType.COMPLICATION,
}


def _get_or_create_node(node_id, node_type, label, description="", metadata=None):
    """Get existing node or create a new one."""
    node, created = KnowledgeGraphNode.objects.get_or_create(
        node_id=node_id,
        defaults={
            "node_type": node_type,
            "label": label,
            "description": description,
            "metadata": metadata or {},
        },
    )
    if not created:
        changed = False
        if node.label != label:
            node.label = label; changed = True
        if node.description != description:
            node.description = description; changed = True
        if changed:
            node.save(update_fields=["label", "description", "updated_at"])
    return node


def _create_edge(source_id, target_id, edge_type, weight=1.0, metadata=None):
    """Create an edge if it doesn't already exist."""
    try:
        source = KnowledgeGraphNode.objects.get(node_id=source_id)
        target = KnowledgeGraphNode.objects.get(node_id=target_id)
    except KnowledgeGraphNode.DoesNotExist:
        logger.warning("Cannot create edge %s->%s: node(s) not found", source_id, target_id)
        return None
    edge, created = KnowledgeGraphEdge.objects.get_or_create(
        source=source, target=target, edge_type=edge_type,
        defaults={"weight": weight, "metadata": metadata or {}},
    )
    return edge


@transaction.atomic
def populate_from_models():
    """Scan all V4.2 knowledge objects and populate the graph.

    Two-pass approach: first create all nodes, then create all edges.
    This avoids ordering issues when edges reference nodes from other types.
    """
    # Pass 1: Create all nodes
    for d in Disease.objects.filter(is_active=True):
        _get_or_create_node(f"d:{d.id}", KnowledgeGraphNode.NodeType.DISEASE, d.name, d.definition[:500] if d.definition else "")
    for syn in Syndrome.objects.filter(is_active=True):
        _get_or_create_node(f"sy:{syn.id}", KnowledgeGraphNode.NodeType.SYNDROME, syn.name, syn.definition[:500] if syn.definition else "")
    for p in PathologyEntity.objects.filter(is_active=True):
        _get_or_create_node(f"p:{p.id}", KnowledgeGraphNode.NodeType.PATHOLOGY, p.name, p.definition[:500] if p.definition else "")
    for l in LabEntity.objects.filter(is_active=True):
        _get_or_create_node(f"l:{l.id}", KnowledgeGraphNode.NodeType.LAB, l.name, l.interpretation[:500] if l.interpretation else "")
    for dr in DrugIntelligence.objects.filter(is_active=True):
        _get_or_create_node(f"dr:{dr.id}", KnowledgeGraphNode.NodeType.DRUG, dr.name, dr.mechanism_of_action[:500] if dr.mechanism_of_action else "")
    for m in MonitoringProtocol.objects.filter(is_active=True):
        _get_or_create_node(f"m:{m.id}", KnowledgeGraphNode.NodeType.MONITORING, m.name)
    for c in Complication.objects.filter(is_active=True):
        _get_or_create_node(f"co:{c.id}", KnowledgeGraphNode.NodeType.COMPLICATION, c.name, c.clinical_features[:500] if c.clinical_features else "")

    # Pass 2: Create all edges (nodes guaranteed to exist)
    for syn in Syndrome.objects.filter(is_active=True).prefetch_related("associated_diseases"):
        for disease in syn.associated_diseases.all():
            _create_edge(f"sy:{syn.id}", f"d:{disease.id}", KnowledgeGraphEdge.EdgeType.CAUSES)

    for p in PathologyEntity.objects.filter(is_active=True).prefetch_related("associated_diseases"):
        for disease in p.associated_diseases.all():
            _create_edge(f"d:{disease.id}", f"p:{p.id}", KnowledgeGraphEdge.EdgeType.DIAGNOSED_BY)
            _create_edge(f"p:{p.id}", f"d:{disease.id}", KnowledgeGraphEdge.EdgeType.FOUND_IN)

    for l in LabEntity.objects.filter(is_active=True).prefetch_related("associated_diseases"):
        for disease in l.associated_diseases.all():
            _create_edge(f"d:{disease.id}", f"l:{l.id}", KnowledgeGraphEdge.EdgeType.DIAGNOSED_BY)

    for dr in DrugIntelligence.objects.filter(is_active=True).prefetch_related("indications"):
        for disease in dr.indications.all():
            _create_edge(f"d:{disease.id}", f"dr:{dr.id}", KnowledgeGraphEdge.EdgeType.TREATED_BY)
            _create_edge(f"dr:{dr.id}", f"d:{disease.id}", KnowledgeGraphEdge.EdgeType.INDICATED_FOR)

    for m in MonitoringProtocol.objects.filter(is_active=True).select_related("drug").prefetch_related("associated_diseases"):
        if m.drug:
            _create_edge(f"dr:{m.drug.id}", f"m:{m.id}", KnowledgeGraphEdge.EdgeType.MONITORED_BY)
        for disease in m.associated_diseases.all():
            _create_edge(f"d:{disease.id}", f"m:{m.id}", KnowledgeGraphEdge.EdgeType.MONITORED_BY)

    for c in Complication.objects.filter(is_active=True).prefetch_related("associated_diseases", "associated_drugs"):
        for disease in c.associated_diseases.all():
            _create_edge(f"d:{disease.id}", f"co:{c.id}", KnowledgeGraphEdge.EdgeType.COMPLICATED_BY)
        for drug in c.associated_drugs.all():
            _create_edge(f"dr:{drug.id}", f"co:{c.id}", KnowledgeGraphEdge.EdgeType.RISK_FACTOR_FOR)

    logger.info("Knowledge graph population complete.")


# ─── Graph Traversal ──────────────────────────────────────────────────────


def find_paths(source_node_id, target_node_type=None, max_depth=4):
    """BFS from source to find all reachable nodes, optionally filtered by type."""
    try:
        start = KnowledgeGraphNode.objects.get(node_id=source_node_id, is_active=True)
    except KnowledgeGraphNode.DoesNotExist:
        return []

    visited = {start.node_id: {"depth": 0, "path": [], "nodes": []}}
    queue = deque([(start, 0, [], [start])])

    results = []
    while queue:
        current, depth, edge_path, node_path = queue.popleft()
        if depth >= max_depth:
            continue

        for edge in current.outgoing_edges.filter(is_active=True).select_related("target"):
            target = edge.target
            if not target.is_active:
                continue
            new_edge_path = edge_path + [edge]
            new_node_path = node_path + [target]

            if target.node_id not in visited or visited[target.node_id]["depth"] > depth + 1:
                visited[target.node_id] = {
                    "depth": depth + 1,
                    "path": new_edge_path,
                    "nodes": new_node_path,
                }
                queue.append((target, depth + 1, new_edge_path, new_node_path))

                if target_node_type is None or target.node_type == target_node_type:
                    results.append({
                        "node": target,
                        "depth": depth + 1,
                        "edge_path": [
                            {
                                "source": e.source.node_id,
                                "target": e.target.node_id,
                                "edge_type": e.edge_type,
                                "weight": e.weight,
                            }
                            for e in new_edge_path
                        ],
                        "node_path": [n.node_id for n in new_node_path],
                    })

    results.sort(key=lambda r: r["depth"])
    return results


def get_reasoning_chain(disease_id, include_related=True):
    """Build a reasoning chain for a disease: syndrome → disease → pathology → labs → drugs → monitoring → complications."""
    disease_node_id = f"d:{disease_id}"
    try:
        disease_node = KnowledgeGraphNode.objects.get(node_id=disease_node_id, is_active=True)
    except KnowledgeGraphNode.DoesNotExist:
        return {"disease_id": disease_id, "error": "Disease not found in graph", "chain": []}

    chain = {"disease_id": disease_id, "disease_label": disease_node.label, "synapses": [], "diagnosis": [], "therapy": [], "monitoring": [], "complications": []}

    # Incoming: syndromes that cause this disease
    for edge in disease_node.incoming_edges.filter(
        edge_type=KnowledgeGraphEdge.EdgeType.CAUSES, is_active=True,
    ).select_related("source"):
        chain["synapses"].append({
            "node_id": edge.source.node_id,
            "label": edge.source.label,
            "relationship": "presents_as",
        })

    # Outgoing: pathology findings
    for edge in disease_node.outgoing_edges.filter(
        edge_type=KnowledgeGraphEdge.EdgeType.DIAGNOSED_BY, is_active=True,
    ).select_related("target"):
        chain["diagnosis"].append({
            "node_id": edge.target.node_id,
            "label": edge.target.label,
            "type": edge.target.node_type,
        })

    # Outgoing: drugs
    for edge in disease_node.outgoing_edges.filter(
        edge_type=KnowledgeGraphEdge.EdgeType.TREATED_BY, is_active=True,
    ).select_related("target"):
        therapy_item = {
            "node_id": edge.target.node_id,
            "label": edge.target.label,
        }
        # Find monitoring protocols for this drug
        monitor_edges = edge.target.outgoing_edges.filter(
            edge_type=KnowledgeGraphEdge.EdgeType.MONITORED_BY, is_active=True,
        ).select_related("target")
        therapy_item["monitoring"] = [
            {"node_id": me.target.node_id, "label": me.target.label}
            for me in monitor_edges
        ]
        chain["therapy"].append(therapy_item)

    # Outgoing: complications
    for edge in disease_node.outgoing_edges.filter(
        edge_type=KnowledgeGraphEdge.EdgeType.COMPLICATED_BY, is_active=True,
    ).select_related("target"):
        chain["complications"].append({
            "node_id": edge.target.node_id,
            "label": edge.target.label,
        })

    # Outgoing: monitoring protocols directly on disease
    for edge in disease_node.outgoing_edges.filter(
        edge_type=KnowledgeGraphEdge.EdgeType.MONITORED_BY, is_active=True,
    ).select_related("target"):
        chain["monitoring"].append({
            "node_id": edge.target.node_id,
            "label": edge.target.label,
        })

    return chain


def get_differential(syndrome_id):
    """Get differential diagnosis for a syndrome."""
    syndrome_node_id = f"sy:{syndrome_id}"
    try:
        syndrome_node = KnowledgeGraphNode.objects.get(node_id=syndrome_node_id, is_active=True)
    except KnowledgeGraphNode.DoesNotExist:
        return {"syndrome_id": syndrome_id, "error": "Syndrome not found in graph", "differentials": []}

    differentials = []
    for edge in syndrome_node.outgoing_edges.filter(
        edge_type=KnowledgeGraphEdge.EdgeType.CAUSES, is_active=True,
    ).select_related("target"):
        differentials.append({
            "node_id": edge.target.node_id,
            "label": edge.target.label,
            "weight": edge.weight,
        })

    return {"syndrome_id": syndrome_id, "differentials": differentials}


def get_graph_summary():
    """Return summary statistics about the knowledge graph."""
    return {
        "total_nodes": KnowledgeGraphNode.objects.filter(is_active=True).count(),
        "total_edges": KnowledgeGraphEdge.objects.filter(is_active=True).count(),
        "nodes_by_type": dict(
            KnowledgeGraphNode.objects.filter(is_active=True)
            .values("node_type")
            .annotate(count=db_models.Count("id"))
            .values_list("node_type", "count")
        ),
        "edges_by_type": dict(
            KnowledgeGraphEdge.objects.filter(is_active=True)
            .values("edge_type")
            .annotate(count=db_models.Count("id"))
            .values_list("edge_type", "count")
        ),
    }
