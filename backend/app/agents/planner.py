import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.ai.model_manager import ModelManager
from app.ai.prompts import PLANNER_PROMPT


class TaskPlanItem(BaseModel):
    id: str = Field(description="Unique task identifier (e.g. task_1)")
    goal: str = Field(description="Actionable task title/goal")
    assigned_agent: str = Field(description="Assigned specialist agent: 'coder', 'researcher', 'planner', 'reviewer', or 'commander'")
    description: Optional[str] = Field(default="", description="Task detail description")
    dependencies: List[str] = Field(default_factory=list, description="List of prerequisite task IDs that must complete first")
    priority: str = Field(default="medium", description="Priority level: low, medium, high, urgent")


class TaskGraphPlan(BaseModel):
    goal: str
    requires_planning: bool = True
    tasks: List[TaskPlanItem]


class PlannerAgent:
    """Upgraded Planner Agent generating validated TaskGraph plans with dependencies."""

    def __init__(self, model_manager: Optional[ModelManager] = None):
        self.model_manager = model_manager or ModelManager()


    async def plan(
        self,
        goal: str,
        strategy_suggestion: Optional[Dict[str, Any]] = None,
        agent_metrics: Optional[List[Dict[str, Any]]] = None
    ) -> TaskGraphPlan:
        schema = {
            "type": "object",
            "properties": {
                "goal": {"type": "string"},
                "requires_planning": {"type": "boolean"},
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "goal": {"type": "string"},
                            "assigned_agent": {"type": "string"},
                            "description": {"type": "string"},
                            "dependencies": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "priority": {"type": "string"}
                        },
                        "required": ["id", "goal", "assigned_agent"]
                    }
                }
            },
            "required": ["goal", "tasks"]
        }
        
        prompt_parts = [f"Goal to plan into structured DAG tasks: {goal}"]
        if strategy_suggestion:
            prompt_parts.append(f"Historical Recommended Strategy: {strategy_suggestion}")
        if agent_metrics:
            prompt_parts.append(f"Agent Historical Performance Metrics: {agent_metrics}")

        prompt = "\n".join(prompt_parts)
        result_dict = await self.model_manager.structured_output(prompt, schema, system_instruction=PLANNER_PROMPT)

        
        # Fallback if structured output parsed generic fallback
        if "tasks" not in result_dict or not isinstance(result_dict["tasks"], list):
            return self._build_default_plan(goal)

        try:
            return TaskGraphPlan.model_validate(result_dict)
        except Exception:
            return self._build_default_plan(goal)

    def _build_default_plan(self, goal: str) -> TaskGraphPlan:
        goal_lower = goal.lower()
        if "code" in goal_lower or "script" in goal_lower or "calculator" in goal_lower:
            return TaskGraphPlan(
                goal=goal,
                requires_planning=True,
                tasks=[
                    TaskPlanItem(id="task_1", goal=f"Generate code for: {goal}", assigned_agent="coder", dependencies=[]),
                    TaskPlanItem(id="task_2", goal="Review generated code quality and safety", assigned_agent="reviewer", dependencies=["task_1"])
                ]
            )
        elif "research" in goal_lower or "compare" in goal_lower or "find" in goal_lower:
            return TaskGraphPlan(
                goal=goal,
                requires_planning=True,
                tasks=[
                    TaskPlanItem(id="task_1", goal=f"Gather web research for: {goal}", assigned_agent="researcher", dependencies=[]),
                    TaskPlanItem(id="task_2", goal="Synthesize findings and review report", assigned_agent="reviewer", dependencies=["task_1"])
                ]
            )
        else:
            return TaskGraphPlan(
                goal=goal,
                requires_planning=True,
                tasks=[
                    TaskPlanItem(id="task_1", goal=goal, assigned_agent="commander", dependencies=[])
                ]
            )
