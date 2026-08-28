from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select, update, delete, func, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    Memory, MemoryEmbeddingModel, MemoryLinkModel, MemoryVersionModel,
    EpisodicMemoryModel, SemanticMemoryModel, ProceduralMemoryModel, PreferenceMemoryModel,
    LearningEventModel, StrategyLibraryModel, StrategyResultModel, AgentMetricModel, ExecutionFeedbackModel
)


class IntelligenceRepository:
    """Repository handling all Phase 6 persistent intelligence data operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Core Memories (5 Categories: WORKING, EPISODIC, SEMANTIC, PROCEDURAL, PREFERENCE)
    # ------------------------------------------------------------------

    async def create_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str = "SEMANTIC",
        importance: int = 1,
        confidence: float = 1.0,
        source: str = "user",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        mem = Memory(
            user_id=user_id,
            memory_type=memory_type.upper(),
            content=content,
            importance=importance,
            confidence=confidence,
            source=source,
            status="ACTIVE",
            metadata_json=metadata or {}
        )
        self.db.add(mem)
        await self.db.commit()
        await self.db.refresh(mem)
        return mem

    async def get_memory_by_id(self, memory_id: str, user_id: Optional[str] = None) -> Optional[Memory]:
        stmt = select(Memory).where(Memory.id == memory_id)
        if user_id:
            stmt = stmt.where(Memory.user_id == user_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_user_memories(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        limit: int = 50,
        status: str = "ACTIVE"
    ) -> List[Memory]:
        stmt = select(Memory).where(Memory.user_id == user_id, Memory.status == status)
        if memory_type:
            stmt = stmt.where(Memory.memory_type == memory_type.upper())
        stmt = stmt.order_by(desc(Memory.importance), desc(Memory.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_memory(
        self,
        memory_id: str,
        user_id: str,
        content: Optional[str] = None,
        importance: Optional[int] = None,
        confidence: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Optional[Memory]:
        mem = await self.get_memory_by_id(memory_id, user_id=user_id)
        if not mem:
            return None

        # Record version before updating
        version_num = (await self._get_max_version(memory_id)) + 1
        ver = MemoryVersionModel(
            memory_id=mem.id,
            version=version_num,
            content=mem.content,
            importance=mem.importance,
            confidence=mem.confidence,
            reason=reason or "update"
        )
        self.db.add(ver)

        if content is not None:
            mem.content = content
        if importance is not None:
            mem.importance = importance
        if confidence is not None:
            mem.confidence = confidence
        mem.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(mem)
        return mem

    async def touch_memory(self, memory_id: str):
        """Update last_accessed timestamp and increment access_count."""
        stmt = select(Memory).where(Memory.id == memory_id)
        res = await self.db.execute(stmt)
        mem = res.scalar_one_or_none()
        if mem:
            mem.last_accessed = datetime.utcnow()
            mem.access_count += 1
            await self.db.commit()

    async def forget_memory(self, memory_id: str, user_id: str) -> bool:
        """Soft-delete memory by setting status to FORGOTTEN."""
        mem = await self.get_memory_by_id(memory_id, user_id=user_id)
        if not mem:
            return False
        mem.status = "FORGOTTEN"
        mem.updated_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def delete_memory(self, memory_id: str, user_id: str) -> bool:
        """Hard-delete memory."""
        mem = await self.get_memory_by_id(memory_id, user_id=user_id)
        if not mem:
            return False
        await self.db.delete(mem)
        await self.db.commit()
        return True

    async def _get_max_version(self, memory_id: str) -> int:
        stmt = select(func.max(MemoryVersionModel.version)).where(MemoryVersionModel.memory_id == memory_id)
        res = await self.db.execute(stmt)
        val = res.scalar()
        return val if val is not None else 0

    # ------------------------------------------------------------------
    # Episodic Memories
    # ------------------------------------------------------------------

    async def record_episodic_memory(
        self,
        user_id: str,
        execution_id: str,
        goal: str,
        plan: Optional[List[Dict[str, Any]]] = None,
        agents_used: Optional[List[str]] = None,
        tools_used: Optional[List[str]] = None,
        execution_steps: Optional[List[Dict[str, Any]]] = None,
        failures: Optional[List[Dict[str, Any]]] = None,
        retries_count: int = 0,
        duration_ms: int = 0,
        final_result: Optional[Dict[str, Any]] = None,
        review_result: Optional[Dict[str, Any]] = None,
        success: bool = True,
        lessons: Optional[List[str]] = None,
        conversation_id: Optional[str] = None
    ) -> EpisodicMemoryModel:
        ep = EpisodicMemoryModel(
            user_id=user_id,
            conversation_id=conversation_id,
            execution_id=execution_id,
            goal=goal,
            plan_json=plan or [],
            agents_used_json=agents_used or [],
            tools_used_json=tools_used or [],
            execution_steps_json=execution_steps or [],
            failures_json=failures or [],
            retries_count=retries_count,
            duration_ms=duration_ms,
            final_result_json=final_result or {},
            review_result_json=review_result or {},
            success=success,
            lessons_json=lessons or []
        )
        self.db.add(ep)
        await self.db.commit()
        await self.db.refresh(ep)
        return ep

    async def get_user_episodic_memories(self, user_id: str, limit: int = 20) -> List[EpisodicMemoryModel]:
        stmt = select(EpisodicMemoryModel).where(
            EpisodicMemoryModel.user_id == user_id
        ).order_by(desc(EpisodicMemoryModel.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # ------------------------------------------------------------------
    # Strategy Library
    # ------------------------------------------------------------------

    async def get_strategies_by_goal_type(self, goal_type: str, limit: int = 5) -> List[StrategyLibraryModel]:
        stmt = select(StrategyLibraryModel).where(
            StrategyLibraryModel.goal_type == goal_type.lower()
        ).order_by(desc(StrategyLibraryModel.success_rate), desc(StrategyLibraryModel.confidence)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_all_strategies(self, limit: int = 50) -> List[StrategyLibraryModel]:
        stmt = select(StrategyLibraryModel).order_by(desc(StrategyLibraryModel.success_rate)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def upsert_strategy(
        self,
        goal_type: str,
        description: str,
        steps: List[Dict[str, Any]],
        agents: List[str],
        tools: List[str],
        success: bool,
        duration_ms: int
    ) -> StrategyLibraryModel:
        goal_key = goal_type.lower()
        stmt = select(StrategyLibraryModel).where(StrategyLibraryModel.goal_type == goal_key)
        res = await self.db.execute(stmt)
        strat = res.scalar_one_or_none()

        if not strat:
            strat = StrategyLibraryModel(
                goal_type=goal_key,
                description=description,
                steps_json=steps,
                agents_json=agents,
                tools_json=tools,
                success_rate=1.0 if success else 0.0,
                sample_count=1,
                average_duration_ms=duration_ms,
                failure_rate=0.0 if success else 1.0,
                confidence=0.8
            )
            self.db.add(strat)
        else:
            prev_samples = strat.sample_count
            new_samples = prev_samples + 1
            prev_succ = strat.success_rate * prev_samples
            new_succ_rate = (prev_succ + (1.0 if success else 0.0)) / new_samples
            
            prev_dur = strat.average_duration_ms * prev_samples
            new_avg_dur = int((prev_dur + duration_ms) / new_samples)

            strat.sample_count = new_samples
            strat.success_rate = new_succ_rate
            strat.failure_rate = 1.0 - new_succ_rate
            strat.average_duration_ms = new_avg_dur
            strat.confidence = min(1.0, 0.5 + (new_samples * 0.05))
            strat.steps_json = steps
            strat.agents_json = agents
            strat.tools_json = tools
            strat.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(strat)
        return strat

    # ------------------------------------------------------------------
    # Agent Metrics
    # ------------------------------------------------------------------

    async def get_all_agent_metrics(self) -> List[AgentMetricModel]:
        stmt = select(AgentMetricModel).order_by(AgentMetricModel.agent_name)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_agent_metrics(
        self,
        agent_name: str,
        success: bool,
        duration_ms: int,
        retries: int = 0,
        tools_used: Optional[List[str]] = None,
        review_score: float = 1.0
    ) -> AgentMetricModel:
        stmt = select(AgentMetricModel).where(AgentMetricModel.agent_name == agent_name)
        res = await self.db.execute(stmt)
        metric = res.scalar_one_or_none()

        if not metric:
            metric = AgentMetricModel(
                agent_name=agent_name,
                total_runs=1,
                successful_runs=1 if success else 0,
                failed_runs=0 if success else 1,
                average_duration_ms=duration_ms,
                total_retries=retries,
                tools_usage_json={t: 1 for t in (tools_used or [])},
                average_review_score=review_score
            )
            self.db.add(metric)
        else:
            n = metric.total_runs + 1
            metric.total_runs = n
            if success:
                metric.successful_runs += 1
            else:
                metric.failed_runs += 1

            metric.average_duration_ms = int(((metric.average_duration_ms * (n - 1)) + duration_ms) / n)
            metric.total_retries += retries

            # Merge tools usage
            usage = dict(metric.tools_usage_json or {})
            for t in (tools_used or []):
                usage[t] = usage.get(t, 0) + 1
            metric.tools_usage_json = usage

            metric.average_review_score = round(((metric.average_review_score * (n - 1)) + review_score) / n, 2)
            metric.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(metric)
        return metric

    # ------------------------------------------------------------------
    # Learning Events
    # ------------------------------------------------------------------

    async def record_learning_event(
        self,
        user_id: str,
        event_type: str,
        observation: Optional[Dict[str, Any]] = None,
        pattern_detected: Optional[str] = None,
        action_taken: Optional[Dict[str, Any]] = None,
        execution_id: Optional[str] = None
    ) -> LearningEventModel:
        evt = LearningEventModel(
            user_id=user_id,
            execution_id=execution_id,
            event_type=event_type,
            observation_json=observation or {},
            pattern_detected=pattern_detected,
            action_taken_json=action_taken or {}
        )
        self.db.add(evt)
        await self.db.commit()
        await self.db.refresh(evt)
        return evt

    async def get_user_learning_events(self, user_id: str, limit: int = 50) -> List[LearningEventModel]:
        stmt = select(LearningEventModel).where(
            LearningEventModel.user_id == user_id
        ).order_by(desc(LearningEventModel.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # ------------------------------------------------------------------
    # Feedback
    # ------------------------------------------------------------------

    async def record_feedback(
        self,
        user_id: str,
        execution_id: str,
        rating: int,
        feedback_text: Optional[str] = None,
        corrected_output: Optional[Dict[str, Any]] = None
    ) -> ExecutionFeedbackModel:
        fb = ExecutionFeedbackModel(
            user_id=user_id,
            execution_id=execution_id,
            rating=rating,
            feedback_text=feedback_text,
            corrected_output_json=corrected_output or {}
        )
        self.db.add(fb)
        await self.db.commit()
        await self.db.refresh(fb)
        return fb
