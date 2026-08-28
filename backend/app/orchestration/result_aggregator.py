import logging
from typing import Dict, List, Any, Optional
from app.orchestration.workflow import WorkflowResult, WorkflowArtifact
from app.intelligence.secret_detector import SecretDetector

logger = logging.getLogger(__name__)

class ResultAggregator:
    """Result Aggregator synthesizing structured workflow execution outcomes."""

    @classmethod
    def aggregate_results(
        cls,
        workflow_id: str,
        goal: str,
        tasks_results: List[Dict[str, Any]],
        artifacts: Optional[List[WorkflowArtifact]] = None,
        sources: Optional[List[Dict[str, Any]]] = None,
        warnings: Optional[List[str]] = None
    ) -> WorkflowResult:
        """Combine task execution outputs into structured WorkflowResult."""
        tasks_completed = sum(1 for t in tasks_results if t.get("status") in ("COMPLETED", "SUCCESS"))
        tasks_failed = sum(1 for t in tasks_results if t.get("status") in ("FAILED", "ERROR"))
        
        overall_status = "COMPLETED" if tasks_failed == 0 else "FAILED"
        if tasks_completed > 0 and tasks_failed > 0:
            overall_status = "PARTIAL_SUCCESS"

        # Formulate concise summary without internal chain-of-thought
        summary = f"Workflow completed with {tasks_completed} task(s) successful and {tasks_failed} failed."
        if overall_status == "COMPLETED":
            summary = f"Goal successfully achieved: {goal}"

        clean_summary = SecretDetector.sanitize_text(summary)
        
        evidence = {
            "task_count": len(tasks_results),
            "completed_tasks": tasks_completed,
            "failed_tasks": tasks_failed,
            "tasks_summary": [
                {
                    "task_id": t.get("task_id"),
                    "agent": t.get("agent"),
                    "status": t.get("status")
                } for t in tasks_results
            ]
        }

        return WorkflowResult(
            id=f"res_{workflow_id}",
            workflow_id=workflow_id,
            summary=clean_summary,
            status=overall_status,
            confidence=1.0 if overall_status == "COMPLETED" else 0.5,
            evidence=evidence,
            artifacts=artifacts or [],
            sources=sources or [],
            tasks_completed=tasks_completed,
            tasks_failed=tasks_failed,
            warnings=warnings or [],
            recommendations=["Store successful strategy in MemoryEngine"] if overall_status == "COMPLETED" else ["Review failure log"]
        )
