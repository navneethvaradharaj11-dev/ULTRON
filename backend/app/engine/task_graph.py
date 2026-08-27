import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.engine.contracts import TaskStatus


class TaskNode:
    """DAG Task Node within an execution TaskGraph."""

    def __init__(
        self,
        task_id: str,
        goal: str,
        assigned_agent: str = "commander",
        description: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        priority: str = "medium",
        max_retries: int = 3,
        input_data: Optional[Dict[str, Any]] = None
    ):
        self.id = task_id
        self.goal = goal
        self.assigned_agent = assigned_agent
        self.description = description or ""
        self.dependencies = dependencies or []
        self.status = TaskStatus.PENDING
        self.priority = priority
        self.retry_count = 0
        self.max_retries = max_retries
        self.input_data = input_data or {}
        self.output_data: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def can_execute(self, completed_task_ids: set[str]) -> bool:
        """Returns True if task is PENDING and all dependencies are completed."""
        if self.status != TaskStatus.PENDING:
            return False
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "description": self.description,
            "assigned_agent": self.assigned_agent,
            "dependencies": self.dependencies,
            "status": self.status.value if isinstance(self.status, TaskStatus) else str(self.status),
            "priority": self.priority,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class TaskGraph:
    """Directed Acyclic Graph (DAG) managing task dependencies and resolution."""

    def __init__(self, execution_id: str, goal: str):
        self.execution_id = execution_id
        self.goal = goal
        self.tasks: Dict[str, TaskNode] = {}

    def add_task(self, task: TaskNode):
        self.tasks[task.id] = task

    def get_task(self, task_id: str) -> Optional[TaskNode]:
        return self.tasks.get(task_id)

    def get_completed_task_ids(self) -> set[str]:
        return {t_id for t_id, task in self.tasks.items() if task.status == TaskStatus.COMPLETED}

    def get_executable_tasks(self) -> List[TaskNode]:
        """Returns list of tasks ready for execution whose prerequisites have completed."""
        completed_ids = self.get_completed_task_ids()
        return [task for task in self.tasks.values() if task.can_execute(completed_ids)]

    def is_complete(self) -> bool:
        """Returns True if all tasks are COMPLETED."""
        if not self.tasks:
            return False
        return all(t.status == TaskStatus.COMPLETED for t in self.tasks.values())

    def is_failed(self) -> bool:
        """Returns True if any task FAILED or CANCELLED."""
        return any(t.status in [TaskStatus.FAILED, TaskStatus.CANCELLED] for t in self.tasks.values())

    def cancel_all(self):
        """Marks all non-completed tasks as CANCELLED."""
        for t in self.tasks.values():
            if t.status in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.WAITING]:
                t.status = TaskStatus.CANCELLED

    def validate_dag(self) -> bool:
        """Validates that there are no circular dependencies in the graph (Kahn's Algorithm)."""
        in_degree = {t_id: len(t.dependencies) for t_id, t in self.tasks.items()}
        queue = [t_id for t_id, deg in in_degree.items() if deg == 0]
        visited_count = 0

        while queue:
            node = queue.pop(0)
            visited_count += 1
            for t_id, t in self.tasks.items():
                if node in t.dependencies:
                    in_degree[t_id] -= 1
                    if in_degree[t_id] == 0:
                        queue.append(t_id)

        return visited_count == len(self.tasks)
