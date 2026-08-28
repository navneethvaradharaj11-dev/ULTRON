import logging
from typing import List, Dict, Any
from app.engine.task_graph import TaskGraph, TaskNode

logger = logging.getLogger(__name__)

class ReplanningEngine:
    """Dynamic DAG re-planning engine for mutating remaining tasks while preserving completed outputs."""

    def __init__(self, max_replans: int = 3):
        self.max_replans = max_replans

    def replan_graph(
        self,
        graph: TaskGraph,
        failed_task_id: str,
        failure_reason: str,
        current_replan_count: int
    ) -> TaskGraph:
        """Modify remaining graph nodes to route around failure while preserving completed tasks."""
        if current_replan_count >= self.max_replans:
            logger.warning("Re-planning limit (%d) reached. Cannot replan graph.", self.max_replans)
            return graph

        logger.info("Replanning DAG graph after failure of task '%s' (Reason: %s)", failed_task_id, failure_reason)

        # Mark failed task as CANCELLED or FAILED
        if failed_task_id in graph.nodes:
            graph.nodes[failed_task_id].status = "FAILED"

        # Identify dependent tasks
        dependent_nodes = [
            n for n in graph.nodes.values()
            if failed_task_id in n.dependencies and n.status == "PENDING"
        ]

        # Add a fallback task node replacing failed task if possible
        replacement_id = f"fallback_{failed_task_id}"
        if replacement_id not in graph.nodes:
            fallback_node = TaskNode(
                task_id=replacement_id,
                goal=f"Alternative resolution for: {graph.nodes[failed_task_id].goal}",
                assigned_agent="commander",
                dependencies=[dep for dep in graph.nodes[failed_task_id].dependencies if dep != failed_task_id]
            )
            graph.add_task(fallback_node)

            # Rewire dependent nodes to rely on replacement node instead of failed node
            for dep_node in dependent_nodes:
                dep_node.dependencies = [replacement_id if d == failed_task_id else d for d in dep_node.dependencies]

        return graph
