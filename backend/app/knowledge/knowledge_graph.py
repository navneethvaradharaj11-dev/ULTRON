import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import KnowledgeEntityModel, KnowledgeRelationshipModel

logger = logging.getLogger("ULTRON.KnowledgeGraph")


class KnowledgeGraph:
    """Topology manager for Knowledge Fabric entity-relationship graph."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_graph(self, user_id: str, workspace_id: str, limit: int = 100) -> Dict[str, Any]:
        """Fetch nodes (entities) and edges (relationships) for workspace."""
        e_stmt = select(KnowledgeEntityModel).where(
            KnowledgeEntityModel.user_id == user_id,
            KnowledgeEntityModel.workspace_id == workspace_id
        ).limit(limit)

        e_res = await self.db.execute(e_stmt)
        entities = list(e_res.scalars().all())

        r_stmt = select(KnowledgeRelationshipModel).where(
            KnowledgeRelationshipModel.user_id == user_id,
            KnowledgeRelationshipModel.workspace_id == workspace_id
        ).limit(limit)

        r_res = await self.db.execute(r_stmt)
        relationships = list(r_res.scalars().all())

        nodes = [
            {
                "id": ent.id,
                "name": ent.name,
                "type": ent.entity_type,
                "confidence": ent.confidence
            } for ent in entities
        ]

        edges = [
            {
                "id": rel.id,
                "source": rel.source_entity_id,
                "target": rel.target_entity_id,
                "relation": rel.relation_type,
                "provenance": rel.provenance
            } for rel in relationships
        ]

        return {
            "workspace_id": workspace_id,
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }
