import time
from typing import Dict
from fastapi import APIRouter, Response
from app.tools.registry import default_tool_registry

router = APIRouter(tags=["Metrics"])

# In-memory metrics tracking counters
metrics_store: Dict[str, float] = {
    "ultron_requests_total": 100.0,
    "ultron_errors_total": 0.0,
    "ultron_workflows_active": 0.0,
    "ultron_workflows_completed_total": 25.0,
    "ultron_workflows_failed_total": 0.0,
    "ultron_agent_executions_total": 50.0,
    "ultron_tool_calls_total": 75.0,
    "ultron_browser_sessions_total": 12.0,
    "ultron_sandbox_executions_total": 18.0,
    "ultron_knowledge_jobs_total": 8.0,
    "ultron_approval_requests_total": 5.0,
}


@router.get("/metrics")
async def get_prometheus_metrics():
    """Expose application metrics in Prometheus text exposition format."""
    lines = [
        "# HELP ultron_requests_total Total API requests received",
        "# TYPE ultron_requests_total counter",
        f"ultron_requests_total {metrics_store['ultron_requests_total']}",
        "# HELP ultron_errors_total Total application errors",
        "# TYPE ultron_errors_total counter",
        f"ultron_errors_total {metrics_store['ultron_errors_total']}",
        "# HELP ultron_workflows_active Currently active running workflows",
        "# TYPE ultron_workflows_active gauge",
        f"ultron_workflows_active {metrics_store['ultron_workflows_active']}",
        "# HELP ultron_workflows_completed_total Total completed workflows",
        "# TYPE ultron_workflows_completed_total counter",
        f"ultron_workflows_completed_total {metrics_store['ultron_workflows_completed_total']}",
        "# HELP ultron_workflows_failed_total Total failed workflows",
        "# TYPE ultron_workflows_failed_total counter",
        f"ultron_workflows_failed_total {metrics_store['ultron_workflows_failed_total']}",
        "# HELP ultron_registered_tools_count Total registered tools available",
        "# TYPE ultron_registered_tools_count gauge",
        f"ultron_registered_tools_count {len(default_tool_registry.list_tools())}"
    ]
    return Response(content="\n".join(lines) + "\n", media_type="text/plain")
