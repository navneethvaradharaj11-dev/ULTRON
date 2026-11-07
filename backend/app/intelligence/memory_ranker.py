import math
from datetime import datetime
from typing import Dict, Any, List, Optional


class MemoryRanker:
    """Computes composite relevance, recency, importance, and confidence scores for candidate memories."""

    @staticmethod
    def score_candidate(
        memory_dict: Dict[str, Any],
        query: str,
        now: Optional[datetime] = None
    ) -> float:
        now = now or datetime.utcnow()

        # 1. Relevance score (0.0 to 1.0) via keyword overlap & jaccard similarity
        content = memory_dict.get("content", "").lower()
        q_words = set(w for w in query.lower().split() if len(w) > 2)
        c_words = set(w for w in content.split() if len(w) > 2)

        if not q_words or not c_words:
            relevance = 0.1
        else:
            intersection = q_words.intersection(c_words)
            union = q_words.union(c_words)
            jaccard = len(intersection) / len(union) if union else 0.0
            overlap = len(intersection) / len(q_words) if q_words else 0.0
            relevance = min(1.0, (jaccard * 0.5) + (overlap * 0.5))

        # 2. Recency score (0.0 to 1.0) exponential decay based on days since created/accessed
        created_str = memory_dict.get("created_at")
        if created_str:
            try:
                created_dt = datetime.fromisoformat(created_str)
                days_old = max(0.0, (now - created_dt).total_seconds() / 86400.0)
            except Exception:
                days_old = 1.0
        else:
            days_old = 1.0
        recency = math.exp(-0.05 * days_old)

        # 3. Importance score (0.0 to 1.0) normalized from 1..5 scale
        imp_raw = float(memory_dict.get("importance", 1))
        importance = min(1.0, max(0.2, imp_raw / 5.0))

        # 4. Confidence score (0.0 to 1.0)
        confidence = float(memory_dict.get("confidence", 1.0))

        # Composite score
        final_score = (relevance * 0.40) + (recency * 0.20) + (importance * 0.20) + (confidence * 0.20)
        return round(final_score, 4)

    @classmethod
    def rank_candidates(
        cls,
        candidates: List[Dict[str, Any]],
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Rank and return top_k candidates with computed scores attached."""
        scored = []
        for cand in candidates:
            score = cls.score_candidate(cand, query)
            c_copy = dict(cand)
            c_copy["score"] = score
            scored.append(c_copy)

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
