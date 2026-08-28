import logging
from typing import List, Dict, Set, Any, Optional
from app.engine.task_graph import TaskGraph, TaskNode

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Intelligent scheduler operating on DAG TaskGraphs with parallel execution group resolution."""

    def __init__(self, graph: TaskGraph):
        self.graph = graph

    def get_ready_tasks(self, completed_task_ids: Set[str], failed_task_ids: Set[str]) -> List[TaskNode]:
        """Return all tasks whose dependencies are fully satisfied and are ready for execution."""
        ready: List[TaskNode] = []
        for task in self.graph.nodes.values():
            if task.task_id in completed_task_ids or task.task_id in failed_task_ids or task.status in ("COMPLETED", "FAILED", "RUNNING", "CANCELLED", "WAITING_APPROVAL"):
                continue


            # Check dependencies
            deps = set(task.dependencies)
            if deps.issubset(completed_task_ids):
                ready.append(task)
            elif deps.intersection(failed_task_ids):
                # Propagate dependency failure
                task.status = "CANCELLED"

        return ready

    def resolve_parallel_groups(self) -> List[List[str]]:
        """Group tasks into parallel execution levels using topological ordering."""
        levels = self.graph.get_execution_levels()
        return [[node.task_id for node in level] for level in levels]

    def is_workflow_complete(self) -> bool:
        """Check if all nodes in the DAG have reached terminal status."""
        for task in self.graph.nodes.values():
            if task.status not in ("COMPLETED", "FAILED", "CANCELLED"):
                return False
        return True

    def get_progress(self) -> float:
        """Calculate percentage completion (0.0 to 1.0)."""
        if not self.graph.nodes:
            return 1.0
        completed = sum(1 for t in self.graph.nodes.values() if t.status == "COMPLETED")
        return completed / len(self.graph.nodes)
