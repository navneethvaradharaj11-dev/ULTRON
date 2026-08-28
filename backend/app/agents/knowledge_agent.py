import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.model_manager import ModelManager
from app.knowledge.knowledge_engine import KnowledgeEngine

logger = logging.getLogger("ULTRON.KnowledgeAgent")


class KnowledgeAgent:
    """Knowledge Agent inspecting workspaces, retrieving structured evidence packages,
    detecting source conflicts, and providing provenance citations.
    """

    def __init__(self, db: AsyncSession, model_manager: Optional[ModelManager] = None):
        self.db = db
        self.model_manager = model_manager or ModelManager()
        self.knowledge_engine = KnowledgeEngine(db)

    async def execute(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Execute knowledge search & synthesis."""
        user_id = "system_user"
        workspace_id = None
        if context and "user_id" in context:
            # Parse context if structured
            pass

        res = await self.knowledge_engine.query_knowledge(
            user_id=user_id,
            query=query,
            workspace_id=workspace_id,
            top_k=5
        )

        return {
            "agent": "knowledge",
            "query": query,
            "citations": res["citations"],
            "evidence_count": len(res["results"]),
            "results": res["results"],
            "conflicts": res["conflicts"]
        }

    async def inspect_workspace_sources(self, user_id: str, workspace_id: str) -> Dict[str, Any]:
        """Inspect workspace sources and entity graph."""
        graph = await self.knowledge_engine.get_workspace_graph(user_id, workspace_id)
        return {
            "workspace_id": workspace_id,
            "entity_count": graph["node_count"],
            "relationship_count": graph["edge_count"],
            "graph": graph
        }
