"""Graph-enhanced clinical reasoning — bridges knowledge graph to reasoning engine.

Provides graph-derived treatment recommendations, monitoring plans, complication
risk profiles, and differential augmentation for the clinical reasoning pipeline.
"""
from __future__ import annotations

import logging
from typing import Any

from .models import KnowledgeGraphNode, KnowledgeGraphEdge
from .graph_service import get_differential, get_reasoning_chain, find_paths

logger = logging.getLogger(__name__)

# Map disease node_ids back to bare IDs (strip "d:" prefix)
DISEASE_PREFIX = "d:"
SYNDROME_PREFIX = "sy:"


def _strip_prefix(node_id: str) -> str:
    return node_id.split(":", 1)[1] if ":" in node_id else node_id


def get_treatment_recommendations(disease_id: str) -> list[dict]:
    """Return graph-derived treatment recommendations for a disease.

    Traverses TREATED_BY edges from the disease node to drug nodes,
    collects drug labels and associated monitoring protocols.
    """
    node_id = f"{DISEASE_PREFIX}{disease_id}"
    try:
        disease_node = KnowledgeGraphNode.objects.get(node_id=node_id, is_active=True)
    except KnowledgeGraphNode.DoesNotExist:
        return []

    treatments = []
    for edge in disease_node.outgoing_edges.filter(
        edge_type=KnowledgeGraphEdge.EdgeType.TREATED_BY, is_active=True,
    ).select_related("target"):
        drug_node = edge.target
        monitoring = [
            {
                "node_id": me.target.node_id,
                "label": me.target.label,
            }
            for me in drug_node.outgoing_edges.filter(
                edge_type=KnowledgeGraphEdge.EdgeType.MONITORED_BY, is_active=True,
            ).select_related("target")
        ]
        treatments.append({
            "drug_id": _strip_prefix(drug_node.node_id),
            "drug_node_id": drug_node.node_id,
            "drug_name": drug_node.label,
            "edge_weight": edge.weight,
            "monitoring": monitoring,
        })

    treatments.sort(key=lambda t: -t["edge_weight"])
    return treatments


def get_monitoring_recommendations(disease_id: str) -> list[dict]:
    """Return graph-derived monitoring protocols for a disease.

    Traverses MONITORED_BY edges directly on the disease node and
    indirectly via TREATED_BY → drug → MONITORED_BY paths.
    """
    node_id = f"{DISEASE_PREFIX}{disease_id}"
    try:
        disease_node = KnowledgeGraphNode.objects.get(node_id=node_id, is_active=True)
    except KnowledgeGraphNode.DoesNotExist:
        return []

    seen: set[str] = set()
    protocols = []

    # Direct disease→monitoring edges
    for edge in disease_node.outgoing_edges.filter(
        edge_type=KnowledgeGraphEdge.EdgeType.MONITORED_BY, is_active=True,
    ).select_related("target"):
        proto = _format_protocol(edge.target)
        if proto["node_id"] not in seen:
            seen.add(proto["node_id"])
            protocols.append(proto)

    # Drug→monitoring edges (indirect via treatments)
    for edge in disease_node.outgoing_edges.filter(
        edge_type=KnowledgeGraphEdge.EdgeType.TREATED_BY, is_active=True,
    ).select_related("target"):
        monitor_edges = edge.target.outgoing_edges.filter(
            edge_type=KnowledgeGraphEdge.EdgeType.MONITORED_BY, is_active=True,
        ).select_related("target")
        for me in monitor_edges:
            proto = _format_protocol(me.target)
            if proto["node_id"] not in seen:
                seen.add(proto["node_id"])
                protocols.append(proto)

    return protocols


def _format_protocol(node: KnowledgeGraphNode) -> dict:
    return {
        "node_id": node.node_id,
        "label": node.label,
        "node_type": node.node_type,
        "description": node.description,
    }


def get_complication_risks(disease_id: str) -> list[dict]:
    """Return graph-derived complication risks for a disease.

    Traverses COMPLICATED_BY edges from the disease node.
    """
    node_id = f"{DISEASE_PREFIX}{disease_id}"
    try:
        disease_node = KnowledgeGraphNode.objects.get(node_id=node_id, is_active=True)
    except KnowledgeGraphNode.DoesNotExist:
        return []

    complications = []
    for edge in disease_node.outgoing_edges.filter(
        edge_type=KnowledgeGraphEdge.EdgeType.COMPLICATED_BY, is_active=True,
    ).select_related("target"):
        complications.append({
            "complication_node_id": edge.target.node_id,
            "complication_name": edge.target.label,
            "description": edge.target.description,
            "edge_weight": edge.weight,
        })

    complications.sort(key=lambda c: -c["edge_weight"])
    return complications


def get_syndrome_matches(features: dict) -> list[dict]:
    """Match clinical features to syndrome nodes in the graph.

    Uses simple keyword overlap between patient features and syndrome
    labels/descriptions to suggest candidate syndromes.
    """
    feature_texts = set()
    for key in ("features", "labs", "biopsy"):
        for item in features.get(key, []):
            feature_texts.add(str(item).lower())
    if features.get("proteinuria") and features["proteinuria"] != "none":
        feature_texts.add(features["proteinuria"].lower())
    if features.get("egfrTrend"):
        feature_texts.add(features["egfrTrend"].lower())

    syndrome_node_type = KnowledgeGraphNode.NodeType.SYNDROME
    candidates = []
    for node in KnowledgeGraphNode.objects.filter(
        node_type=syndrome_node_type, is_active=True,
    ).only("node_id", "label", "description"):
        label_lower = node.label.lower()
        desc_lower = (node.description or "").lower()
        score = sum(
            1 for ft in feature_texts
            if ft in label_lower or ft in desc_lower
        )
        if score > 0:
            candidates.append({
                "syndrome_node_id": node.node_id,
                "syndrome_name": node.label,
                "match_score": score,
            })

    candidates.sort(key=lambda c: -c["match_score"])
    return candidates


def get_graph_differential(features: dict) -> list[dict]:
    """Generate a differential diagnosis list from the graph.

    First matches syndromes from features, then traverses CAUSES edges
    to find diseases. Returns ranked diseases with their syndromes.
    """
    syndromes = get_syndrome_matches(features)
    if not syndromes:
        return []

    disease_map: dict[str, dict] = {}
    for syn in syndromes:
        diff = get_differential(_strip_prefix(syn["syndrome_node_id"]))
        for d in diff.get("differentials", []):
            did = d["node_id"]
            if did not in disease_map:
                disease_map[did] = {
                    "disease_node_id": did,
                    "disease_name": d["label"],
                    "graph_weight": d["weight"],
                    "from_syndromes": [],
                }
            disease_map[did]["from_syndromes"].append(syn["syndrome_name"])

    result = sorted(disease_map.values(), key=lambda x: -x["graph_weight"])
    return result


def augment_differential(
    differential: list[dict],
    patient_features: dict,
) -> list[dict]:
    """Augment a rule-based differential with graph-derived diseases.

    Merges graph diseases into the differential list; if a disease already
    exists (matched by node_id), adds graph metadata.
    """
    graph_diseases = get_graph_differential(patient_features)

    existing_ids = {d.get("disease_id") or d.get("disease_node_id", "") for d in differential}
    augmented = list(differential)

    for gd in graph_diseases:
        did = _strip_prefix(gd["disease_node_id"])
        if did not in existing_ids:
            augmented.append({
                "disease_id": did,
                "disease_name": gd["disease_name"],
                "score": 0,
                "matched_rules_count": 0,
                "source": "knowledge_graph",
                "evidence_grade": "NG",
                "graph_weight": gd["graph_weight"],
                "from_syndromes": gd["from_syndromes"],
            })
            existing_ids.add(did)
        else:
            for entry in augmented:
                if (entry.get("disease_id") or entry.get("disease_node_id", "")) == did:
                    entry.setdefault("graph_weight", gd["graph_weight"])
                    entry.setdefault("from_syndromes", gd["from_syndromes"])
                    break

    return augmented


def build_graph_reasoning_steps(disease_id: str) -> list[dict]:
    """Build reasoning chain steps from graph traversal for explainability.

    Returns a list of step dicts compatible with the profile.reasoning_chain format.
    """
    chain = get_reasoning_chain(disease_id)
    if "error" in chain:
        return []

    steps = []

    if chain.get("synapses"):
        steps.append({
            "step": "graph_syndrome_association",
            "finding": f"Associated with {len(chain['synapses'])} syndrome(s)",
            "detail": [s["label"] for s in chain["synapses"]],
            "confidence": "high",
        })

    if chain.get("diagnosis"):
        steps.append({
            "step": "graph_diagnostic_evidence",
            "finding": f"{len(chain['diagnosis'])} diagnostic finding(s) in knowledge graph",
            "detail": [d["label"] for d in chain["diagnosis"][:5]],
            "confidence": "moderate",
        })

    if chain.get("therapy"):
        steps.append({
            "step": "graph_treatment_options",
            "finding": f"{len(chain['therapy'])} treatment option(s) available",
            "detail": [t["label"] for t in chain["therapy"]],
            "confidence": "moderate",
        })

    if chain.get("monitoring"):
        steps.append({
            "step": "graph_monitoring_plan",
            "finding": f"{len(chain['monitoring'])} monitoring protocol(s) recommended",
            "detail": [m["label"] for m in chain["monitoring"]],
            "confidence": "high",
        })

    if chain.get("complications"):
        steps.append({
            "step": "graph_complication_risks",
            "finding": f"{len(chain['complications'])} complication risk(s) identified",
            "detail": [c["label"] for c in chain["complications"]],
            "confidence": "moderate",
        })

    return steps


def enhance_treatment_plan(disease_id: str) -> dict:
    """Build a comprehensive treatment plan from the graph for a disease.

    Combines drug recommendations, monitoring protocols, and complication
    awareness into a single treatment plan dict.
    """
    return {
        "disease_id": disease_id,
        "treatments": get_treatment_recommendations(disease_id),
        "monitoring": get_monitoring_recommendations(disease_id),
        "complication_risks": get_complication_risks(disease_id),
    }