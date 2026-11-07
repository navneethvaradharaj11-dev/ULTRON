import pytest
from app.autonomy.contracts import AutonomyLevel, DecisionType
from app.autonomy.autonomy_policy import AutonomyPolicyEngine
from app.engine.task_graph import TaskGraph, TaskNode
from app.intelligence.memory_ranker import MemoryRanker
from app.core.intent_engine import IntentEngine
from app.security.unified_security import UnifiedSecurityGate


from app.engine.contracts import TaskStatus

def test_1_autonomous_dag_planning_and_dependencies():
    """Verify multi-step planning and DAG dependency resolution."""
    tg = TaskGraph(execution_id="exec_test_001", goal="Automated data pipeline")
    t1 = TaskNode("fetch_data", "Fetch data from source", "researcher")
    t2 = TaskNode("process_data", "Process fetched data", "coder", dependencies=["fetch_data"])
    t3 = TaskNode("review_results", "Review final output", "reviewer", dependencies=["process_data"])

    tg.add_task(t1)
    tg.add_task(t2)
    tg.add_task(t3)

    assert tg.validate_dag() is True
    ready_initial = tg.get_executable_tasks()
    assert len(ready_initial) == 1
    assert ready_initial[0].id == "fetch_data"

    # Complete task 1
    t1.status = TaskStatus.COMPLETED
    ready_after_t1 = tg.get_executable_tasks()
    assert len(ready_after_t1) == 1
    assert ready_after_t1[0].id == "process_data"


def test_2_intelligent_task_prioritization_and_intent():
    """Verify intent engine parses risk, urgency, and required capabilities."""
    high_intent = IntentEngine.parse_intent("Delete the temporary build files in production")
    assert high_intent.risk_level in ["HIGH", "CRITICAL"]
    assert high_intent.required_approval is True

    low_intent = IntentEngine.parse_intent("What is the current time and system health?")
    assert low_intent.risk_level == "LOW"
    assert low_intent.required_approval is False


def test_3_human_in_the_loop_approval_gate():
    """Verify high-risk actions are blocked by security policy requiring explicit approval."""
    is_sensitive, risk_msg = UnifiedSecurityGate.evaluate_command_risk("HIGH", True)
    assert is_sensitive is True
    assert "sensitive" in risk_msg or "approval" in risk_msg

    is_safe, _ = UnifiedSecurityGate.evaluate_command_risk("LOW", False)
    assert is_safe is False


def test_4_persistent_memory_contextual_ranking():
    """Verify semantic memory ranking balances importance, recency, and decay."""
    memories = [
        {"id": "m1", "content": "User prefers concise Python code", "importance": 5, "created_at": "2026-11-01T00:00:00"},
        {"id": "m2", "content": "Temporary scratch note", "importance": 1, "created_at": "2026-10-01T00:00:00"},
        {"id": "m3", "content": "User timezone is Asia/Kolkata", "importance": 4, "created_at": "2026-11-05T00:00:00"}
    ]

    ranked = MemoryRanker.rank_candidates(memories, query="What is the user's coding preference?")
    assert len(ranked) == 3
    assert ranked[0]["id"] == "m1"  # Highest relevance and importance


def test_5_proactive_assistance_autonomy_eval():
    """Verify autonomous event triggers are categorized into notify vs workflow according to level."""
    # Level 1 notifies operator
    d1, _ = AutonomyPolicyEngine.evaluate_policy(AutonomyLevel.LEVEL_1, "FILE_CHANGE")
    assert d1 == DecisionType.NOTIFY

    # Level 2 initiates automated remediation workflow
    d2, _ = AutonomyPolicyEngine.evaluate_policy(AutonomyLevel.LEVEL_2, "FILE_CHANGE")
    assert d2 == DecisionType.START_WORKFLOW
