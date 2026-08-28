import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import KnowledgeChunkModel, KnowledgeSourceModel
from app.knowledge.semantic_search import SemanticSearch
from app.knowledge.citation_engine import CitationEngine

logger = logging.getLogger("ULTRON.HybridSearch")


class HybridSearch:
    """Hybrid Search combining BM25 keyword matching and vector semantic similarity with reranking and citations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.semantic_search = SemanticSearch(db)

    async def search(
        self,
        user_id: str,
        query: str,
        workspace_id: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        # 1. Semantic Vector Search
        semantic_results = await self.semantic_search.search(user_id=user_id, query=query, workspace_id=workspace_id, top_k=top_k * 2)

        # 2. Keyword Search
        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        
        stmt = select(
            KnowledgeChunkModel,
            KnowledgeSourceModel
        ).join(
            KnowledgeSourceModel, KnowledgeChunkModel.source_id == KnowledgeSourceModel.id
        ).where(
            KnowledgeChunkModel.user_id == user_id
        )

        if workspace_id:
            stmt = stmt.where(KnowledgeSourceModel.workspace_id == workspace_id)

        res = await self.db.execute(stmt)
        all_chunks = res.all()

        keyword_results = []
        for chunk, source in all_chunks:
            c_text = chunk.content.lower()
            matches = sum(1 for term in query_terms if term in c_text)
            if matches > 0:
                kw_score = matches / max(len(query_terms), 1)
                loc_spec = chunk.location_json.get("location", "Document") if chunk.location_json else "Document"
                keyword_results.append({
                    "chunk_id": chunk.id,
                    "source_id": source.id,
                    "filename": source.filename,
                    "content": chunk.content,
                    "location_spec": loc_spec,
                    "score": kw_score
                })

        # 3. Hybrid Reranking (50% Semantic + 50% Keyword)
        combined: Dict[str, Dict[str, Any]] = {}

        for s_res in semantic_results:
            cid = s_res["chunk_id"]
            combined[cid] = s_res
            combined[cid]["final_score"] = s_res["score"] * 0.5

        for k_res in keyword_results:
            cid = k_res["chunk_id"]
            if cid in combined:
                combined[cid]["final_score"] += k_res["score"] * 0.5
            else:
                k_res["final_score"] = k_res["score"] * 0.5
                combined[cid] = k_res

        sorted_list = sorted(combined.values(), key=lambda x: x["final_score"], reverse=True)[:top_k]

        # 4. Attach Traceable Citations
        results_with_citations = []
        for idx, item in enumerate(sorted_list, 1):
            citation = CitationEngine.format_citation(
                index=idx,
                filename=item["filename"],
                location_spec=item["location_spec"]
            )
            item["citation"] = citation
            results_with_citations.append(item)

        return results_with_citations
