from app.orchestration.recovery_engine import RecoveryEngine

def test_recovery_engine_actions():
    # Security failure action must be STOP
    res_sec = RecoveryEngine.determine_recovery_action("SECURITY_FAILURE", "t1", "coder", 0)
    assert res_sec["action"] == "STOP"

    # Retry action for transient timeout
    res_to = RecoveryEngine.determine_recovery_action("TIMEOUT", "t1", "browser_agent", 0)
    assert res_to["action"] == "RETRY_TASK"
    assert res_to["new_retry_count"] == 1

    # Max retries reached action
    res_max = RecoveryEngine.determine_recovery_action("TIMEOUT", "t1", "browser_agent", 3, max_retries=3)
    assert res_max["action"] == "REPLAN_OR_FAIL"
