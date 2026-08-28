import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.intelligence_repo import IntelligenceRepository
from app.database.models import SemanticMemoryModel, ProceduralMemoryModel, PreferenceMemoryModel

logger = logging.getLogger("ULTRON.MemoryConsolidator")


class MemoryConsolidator:
    """Consolidation engine that converts repeated observations into stable,
    structured semantic, procedural, and preference memories with conflict detection.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IntelligenceRepository(db)

    async def consolidate_observations(
        self,
        user_id: str,
        observations: List[Dict[str, Any]],
        category: str = "SEMANTIC"
    ) -> Dict[str, Any]:
        """Consolidate short-term observations into structured long-term memory."""
        if not user_id:
            raise ValueError("user_id is required for memory consolidation.")

        category = category.upper()
        if not observations:
            return {"status": "NO_OP", "consolidated_count": 0}

        consolidated_items = []
        conflicts_detected = []

        if category == "SEMANTIC":
            # Group observations by topic
            topic_map: Dict[str, List[str]] = {}
            for obs in observations:
                topic = obs.get("topic", "General").title()
                fact = obs.get("fact") or obs.get("content") or str(obs)
                topic_map.setdefault(topic, []).append(fact)

            for topic, facts in topic_map.items():
                # Conflict detection: check if existing topic has contradicting facts
                existing_stmt = select(SemanticMemoryModel).where(
                    SemanticMemoryModel.user_id == user_id,
                    SemanticMemoryModel.topic == topic
                )
                res = await self.db.execute(existing_stmt)
                existing = res.scalar_one_or_none()

                if existing:
                    # Merge unique facts
                    current_facts = list(existing.facts_json or [])
                    new_unique = [f for f in facts if f not in current_facts]
                    if new_unique:
                        existing.facts_json = current_facts + new_unique
                        existing.confidence = min(1.0, existing.confidence + 0.05)
                        existing.updated_at = datetime.utcnow()
                        consolidated_items.append({"topic": topic, "facts": existing.facts_json})
                else:
                    sem = SemanticMemoryModel(
                        user_id=user_id,
                        topic=topic,
                        concept=f"{topic} Concept Overview",
                        facts_json=facts,
                        confidence=0.9,
                        source="consolidation_engine"
                    )
                    self.db.add(sem)
                    consolidated_items.append({"topic": topic, "facts": facts})

            await self.db.commit()

        elif category == "PREFERENCE":
            for obs in observations:
                key = obs.get("key", "").lower().strip()
                val = obs.get("value", "").strip()
                if not key or not val:
                    continue

                existing_pref = await self._get_preference(user_id, key)
                if existing_pref:
                    if existing_pref.value != val:
                        # Conflict detected! Do not blindly overwrite — increment version / update confidence
                        conflicts_detected.append({
                            "key": key, "old_value": existing_pref.value, "new_value": val
                        })
                        existing_pref.value = val
                        existing_pref.confidence = round(min(1.0, existing_pref.confidence + 0.05), 2)
                        existing_pref.updated_at = datetime.utcnow()
                else:
                    pref = PreferenceMemoryModel(
                        user_id=user_id,
                        key=key,
                        value=val,
                        confidence=0.95,
                        source="consolidation_engine"
                    )
                    self.db.add(pref)
                    consolidated_items.append({"key": key, "value": val})

            await self.db.commit()

        # Create structured memory entry in core memories
        summary_text = f"Consolidated {len(consolidated_items)} items for category {category}."
        await self.repo.create_memory(
            user_id=user_id,
            content=summary_text,
            memory_type=category,
            importance=3,
            confidence=0.9,
            source="memory_consolidator"
        )

        return {
            "status": "SUCCESS",
            "category": category,
            "consolidated_count": len(consolidated_items),
            "conflicts_detected": conflicts_detected
        }

    async def _get_preference(self, user_id: str, key: str) -> Optional[PreferenceMemoryModel]:
        stmt = select(PreferenceMemoryModel).where(
            PreferenceMemoryModel.user_id == user_id,
            PreferenceMemoryModel.key == key
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


from datetime import datetime
from sqlalchemy import select
