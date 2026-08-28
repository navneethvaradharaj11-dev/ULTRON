import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.knowledge_repo import KnowledgeRepository
from app.knowledge.source_manager import SourceManager
from app.knowledge.ingestion_engine import IngestionEngine
from app.knowledge.hybrid_search import HybridSearch
from app.knowledge.knowledge_graph import KnowledgeGraph
from app.knowledge.citation_engine import CitationEngine
from app.intelligence.secret_detector import SecretDetector

logger = logging.getLogger("ULTRON.KnowledgeEngine")


class KnowledgeEngine:
    """Central Knowledge Engine orchestrating workspace sources, ingestion, search, knowledge graph, and citations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = KnowledgeRepository(db)
        self.source_manager = SourceManager(db)
        self.ingestion_engine = IngestionEngine(db)
        self.hybrid_search = HybridSearch(db)
        self.knowledge_graph = KnowledgeGraph(db)

    async def create_workspace(self, user_id: str, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        ws = await self.repo.create_workspace(user_id, name, description)
        return {
            "workspace_id": ws.id,
            "name": ws.name,
            "description": ws.description,
            "created_at": ws.created_at.isoformat()
        }

    async def list_workspaces(self, user_id: str) -> List[Dict[str, Any]]:
        workspaces = await self.repo.list_workspaces(user_id)
        return [
            {
                "workspace_id": ws.id,
                "name": ws.name,
                "description": ws.description,
                "created_at": ws.created_at.isoformat()
            } for ws in workspaces
        ]

    async def upload_and_ingest_source(
        self,
        user_id: str,
        workspace_id: str,
        filename: str,
        content_bytes: bytes,
        mime_type: str,
        origin: str = "upload"
    ) -> Dict[str, Any]:
        """Save source file in sandbox, perform deduplication, and execute ingestion pipeline."""
        src, is_duplicate = await self.source_manager.register_source_file(
            user_id=user_id,
            workspace_id=workspace_id,
            filename=filename,
            content_bytes=content_bytes,
            mime_type=mime_type,
            origin=origin
        )

        if is_duplicate:
            return {
                "source_id": src.id,
                "filename": src.filename,
                "status": src.status,
                "deduplicated": True,
                "message": "Source content already exists in workspace."
            }

        ingest_res = await self.ingestion_engine.process_source(src.id, user_id)
        return {
            "source_id": src.id,
            "filename": src.filename,
            "status": ingest_res["status"],
            "chunks_created": ingest_res["chunks_created"],
            "deduplicated": False
        }

    async def query_knowledge(
        self,
        user_id: str,
        query: str,
        workspace_id: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Perform hybrid search and build evidence package with citations."""
        results = await self.hybrid_search.search(user_id=user_id, query=query, workspace_id=workspace_id, top_k=top_k)
        evidence_pkg = CitationEngine.generate_evidence_package(results)

        # Detect potential contradictions / conflicts
        conflicts = self._detect_conflicts(results)

        return {
            "query": query,
            "results": results,
            "citations": evidence_pkg["citations"],
            "evidence": evidence_pkg["evidence"],
            "conflicts": conflicts
        }

    async def get_workspace_graph(self, user_id: str, workspace_id: str) -> Dict[str, Any]:
        return await self.knowledge_graph.get_graph(user_id, workspace_id)

    async def delete_source(self, source_id: str, user_id: str) -> bool:
        return await self.source_manager.delete_source_and_cleanup(source_id, user_id)

    def _detect_conflicts(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify potential evidence conflicts between different knowledge sources."""
        conflicts = []
        if len(results) < 2:
            return conflicts

        for i in range(len(results) - 1):
            r1 = results[i]
            r2 = results[i + 1]
            c1 = r1.get("content", "").lower()
            c2 = r2.get("content", "").lower()
            
            # Simple conflict detection heuristic
            if "version" in c1 and "version" in c2 and r1.get("filename") != r2.get("filename"):
                if c1 != c2:
                    conflicts.append({
                        "source_1": r1.get("filename"),
                        "source_2": r2.get("filename"),
                        "conflict_type": "VERSION_DISCREPANCY",
                        "description": f"Potential discrepancy between '{r1.get('filename')}' and '{r2.get('filename')}'"
                    })
        return conflicts
