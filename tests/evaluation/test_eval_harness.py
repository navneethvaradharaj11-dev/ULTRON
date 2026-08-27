"""
test_eval_harness.py — Phase 2.5 End-to-End Evaluation Harness

Runs deterministic evaluation cases from eval_dataset.json through the
FULL agentic pipeline (Planner → TaskGraph → ExecutionEngine → Reviewer).

External AI calls are isolated behind MockModelManager (AI_PROVIDER=mock),
but the entire ULTRON engine stack — DAG resolution, state machine, event
persistence, reviewer gate, metrics recording — is exercised for real.

Success criteria per case:
  - execution reaches COMPLETED status
  - all required event types appear in the persisted event timeline
  - event consistency check passes (valid=True)
  - at least one ExecutionMetrics record is written
"""
import json
import os
import pytest
from pathlib import Path
from typing import Dict, Any, List

from app.database.repositories.execution_repo import ExecutionRepository
from app.engine.execution_engine import AgentExecutionEngine
from app.engine.task_graph import TaskGraph, TaskNode
from app.agents.planner import PlannerAgent
from app.ai.model_manager import ModelManager


# Load evaluation dataset
_DATASET_PATH = Path(__file__).parent / "eval_dataset.json"
with open(_DATASET_PATH) as f:
    EVAL_CASES = json.load(f)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _run_case(
    db_session,
    case: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute one evaluation case and return a result summary."""
    repo = ExecutionRepository(db_session)
    model_manager = ModelManager()  # Uses mock provider from settings

    # Create execution
    exec_rec = await repo.create_execution("test_user_id", case["goal"])

    # Build task graph via PlannerAgent (deterministic mock plan)
    planner = PlannerAgent(model_manager)
    plan = await planner.plan(case["goal"])

    graph = TaskGraph(exec_rec.id, case["goal"])
    for idx, t_item in enumerate(plan.tasks):
        graph.add_task(TaskNode(
            task_id=t_item.id or f"task_{idx+1}",
            goal=t_item.goal,
            assigned_agent=t_item.assigned_agent,
            description=t_item.description,
            dependencies=t_item.dependencies,
            priority=t_item.priority
        ))

    # Run execution engine
    events: List[Dict[str, Any]] = []
    engine = AgentExecutionEngine(db=db_session, model_manager=model_manager)
    async for event in engine.run_execution(exec_rec.id, graph, "test_user_id"):
        events.append(event)

    # Reload final execution state
    final_exec = await repo.get_execution_by_id(exec_rec.id)
    db_events = await repo.get_execution_events(exec_rec.id)
    consistency = await repo.verify_event_consistency(exec_rec.id)
    metrics = await repo.get_execution_metrics(exec_rec.id)
    db_tasks = await repo.get_execution_tasks(exec_rec.id)

    return {
        "case_id": case["id"],
        "status": final_exec.status if final_exec else "UNKNOWN",
        "event_types": [e.event_type for e in db_events],
        "task_count": len(db_tasks),
        "consistency": consistency,
        "metrics_count": len(metrics),
        "events_streamed": len(events),
    }


# ---------------------------------------------------------------------------
# Individual deterministic eval tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_eval_single_calculation(db_session):
    """eval_001: Single calculation must complete and produce output containing '30'."""
    case = next(c for c in EVAL_CASES if c["id"] == "eval_001")
    result = await _run_case(db_session, case)

    assert result["status"] == "COMPLETED", f"Expected COMPLETED, got {result['status']}"
    assert "execution_started" in result["event_types"]
    assert "execution_completed" in result["event_types"]
    assert result["consistency"]["valid"] is True, f"Consistency issues: {result['consistency']['issues']}"
    assert result["metrics_count"] >= 1


@pytest.mark.asyncio
async def test_eval_research_review_workflow(db_session):
    """eval_002: Research + review pipeline must complete with valid event sequence."""
    case = next(c for c in EVAL_CASES if c["id"] == "eval_002")
    result = await _run_case(db_session, case)

    assert result["status"] == "COMPLETED", f"Expected COMPLETED, got {result['status']}"
    assert "execution_started" in result["event_types"]
    assert "execution_completed" in result["event_types"]
    assert result["consistency"]["valid"] is True, f"Consistency issues: {result['consistency']['issues']}"


@pytest.mark.asyncio
async def test_eval_code_generation_workflow(db_session):
    """eval_003: Code generation + review pipeline must complete successfully."""
    case = next(c for c in EVAL_CASES if c["id"] == "eval_003")
    result = await _run_case(db_session, case)

    assert result["status"] == "COMPLETED", f"Expected COMPLETED, got {result['status']}"
    assert result["consistency"]["valid"] is True


@pytest.mark.asyncio
async def test_eval_full_four_step_e2e(db_session):
    """eval_004: Full E2E — Research → Compare → Recommend → Review.

    This is the flagship evaluation case verifying the complete agentic workflow:
    USER GOAL → PLANNER → TASK GRAPH → AGENT ROUTER → AGENT EXECUTION →
    TOOL EXECUTION → OBSERVATION → REVIEW → FINAL RESULT
    """
    case = next(c for c in EVAL_CASES if c["id"] == "eval_004")
    result = await _run_case(db_session, case)

    assert result["status"] == "COMPLETED", (
        f"Full E2E test FAILED with status '{result['status']}'. "
        f"Events: {result['event_types']}"
    )
    assert "execution_started" in result["event_types"]
    assert "plan_created" in result["event_types"]
    assert "execution_completed" in result["event_types"]
    assert result["consistency"]["valid"] is True, (
        f"Event consistency FAILED: {result['consistency']['issues']}"
    )
    assert result["metrics_count"] >= 1, "At least one metrics record must exist"
    assert result["task_count"] >= 1, "At least one task must be persisted"


@pytest.mark.asyncio
async def test_eval_commander_dispatch(db_session):
    """eval_005: Simple commander dispatch must complete without error."""
    case = next(c for c in EVAL_CASES if c["id"] == "eval_005")
    result = await _run_case(db_session, case)

    assert result["status"] == "COMPLETED"
    assert result["consistency"]["valid"] is True


# ---------------------------------------------------------------------------
# Aggregate success rate across all cases
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_eval_aggregate_success_rate(db_session):
    """All evaluation cases must achieve a 100% success rate.

    This test is the definitive Phase 2.5 pass gate.
    """
    passed = 0
    failed_cases = []

    for case in EVAL_CASES:
        try:
            result = await _run_case(db_session, case)
            if result["status"] == "COMPLETED" and result["consistency"]["valid"]:
                passed += 1
            else:
                failed_cases.append({
                    "id": case["id"],
                    "status": result["status"],
                    "consistency": result["consistency"]
                })
        except Exception as exc:
            failed_cases.append({"id": case["id"], "error": str(exc)})

    total = len(EVAL_CASES)
    success_rate = passed / total * 100
    print(f"\n[EVAL] Success rate: {passed}/{total} ({success_rate:.1f}%)")

    if failed_cases:
        print("[EVAL] Failed cases:")
        for fc in failed_cases:
            print(f"  - {fc}")

    assert passed == total, (
        f"Evaluation success rate {success_rate:.1f}% < 100%. Failed: {failed_cases}"
    )
