"""Build (or refresh) the clinical knowledge graph from the curated entities.

The reasoning engine's graph layer (differential augmentation, graph reasoning
steps, treatment-plan enhancement) reads KnowledgeGraphNode / KnowledgeGraphEdge.
Those are derived from the already-seeded Disease / Syndrome / Pathology / Lab /
Drug / Monitoring / Complication rows via ``graph_service.populate_from_models``,
but nothing in the seed flow ran it — so a fresh install had an empty graph and
the graph layer produced nothing. This command builds it, and is idempotent
(get_or_create), so it is safe to re-run after every KB seed/version bump.
"""
from __future__ import annotations

from django.core.management.base import BaseCommand

from knowledge.graph_service import populate_from_models
from knowledge.models import KnowledgeGraphNode, KnowledgeGraphEdge


class Command(BaseCommand):
    help = "Build/refresh the knowledge graph (nodes + edges) from curated entities."

    def handle(self, *args, **options):
        before_nodes = KnowledgeGraphNode.objects.count()
        before_edges = KnowledgeGraphEdge.objects.count()

        populate_from_models()

        nodes = KnowledgeGraphNode.objects.count()
        edges = KnowledgeGraphEdge.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Knowledge graph built: {nodes} nodes (+{nodes - before_nodes}), "
            f"{edges} edges (+{edges - before_edges})."
        ))
