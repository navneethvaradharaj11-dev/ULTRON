import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.commander import CommanderAgent
from app.agents.planner import PlannerAgent
from app.intelligence.memory_engine import MemoryEngine
from app.intelligence.strategy_engine import StrategyEngine
from app.engine.task_graph import TaskGraph

logger = logging.getLogger(__name__)

class WorkflowPlanner:
    """Intelligent workflow planner integrating Commander, Memory, Strategy, and Planner Agents."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.commander = CommanderAgent()
        self.planner = PlannerAgent()
        self.memory_engine = MemoryEngine(db)
        self.strategy_engine = StrategyEngine(db)

    async def plan_workflow(
        self,
        user_id: str,
        goal: str,
        execution_id: str
    ) -> Dict[str, Any]:
        """Lifecycle step: Understand goal -> Lookup memory -> Select strategy -> Build TaskGraph."""
        # 1. Understand Goal
        intent = await self.commander.analyze_intent(goal)
        goal_type = intent.get("intent", "general_execution")

        # 2. Memory Lookup
        memories = await self.memory_engine.retrieve_memories(
            user_id=user_id,
            query=goal,
            limit=5
        )
        memory_texts = [m["content"] for m in memories]

        # 3. Strategy Selection
        strategy = await self.strategy_engine.best_strategy(goal_type)
        strategy_id = strategy["id"] if strategy else None

        # 4. Generate Structured Plan
        plan_res_obj = await self.planner.plan(
            goal=goal,
            strategy_suggestion=strategy
        )

        plan_nodes = [t.model_dump() for t in plan_res_obj.tasks]


        # 5. Build and Validate DAG
        graph = TaskGraph(execution_id=execution_id, goal=goal)
        for node_data in plan_nodes:
            tid = node_data.get("task_id") or node_data.get("id") or "task_1"
            from app.engine.task_graph import TaskNode
            node = TaskNode(
                task_id=tid,
                goal=node_data["goal"],
                assigned_agent=node_data.get("assigned_agent", "commander"),
                dependencies=node_data.get("dependencies", []),
                priority=node_data.get("priority", "medium")
            )
            graph.add_task(node)
            node_data["task_id"] = tid


        if not graph.validate_dag():
            raise ValueError("Generated plan is invalid DAG (contains circular dependencies)")


        return {
            "intent": intent,
            "strategy_id": strategy_id,
            "strategy": strategy,
            "memories_used": memory_texts,
            "plan_nodes": plan_nodes,
            "graph": graph
        }
