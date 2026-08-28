import pytest
from app.autonomy.contracts import AutonomyLevel, DecisionType
from app.autonomy.autonomy_policy import AutonomyPolicyEngine


def test_level_0_observe_only():
    dtype, reason = AutonomyPolicyEngine.evaluate_policy(AutonomyLevel.LEVEL_0, "WEB_CHANGE")
    assert dtype == DecisionType.IGNORE
    assert "OBSERVE_ONLY" in reason


def test_level_1_notify_only():
    dtype, reason = AutonomyPolicyEngine.evaluate_policy(AutonomyLevel.LEVEL_1, "WEB_CHANGE")
    assert dtype == DecisionType.NOTIFY


def test_level_2_low_risk_action():
    dtype, reason = AutonomyPolicyEngine.evaluate_policy(AutonomyLevel.LEVEL_2, "FILE_CHANGE")
    assert dtype == DecisionType.START_WORKFLOW


def test_level_3_approval_required():
    dtype, reason = AutonomyPolicyEngine.evaluate_policy(AutonomyLevel.LEVEL_3, "EXTERNAL_MESSAGE")
    assert dtype == DecisionType.REQUIRE_APPROVAL


def test_level_4_forbidden():
    dtype, reason = AutonomyPolicyEngine.evaluate_policy(AutonomyLevel.LEVEL_4, "CREDENTIAL_EXTRACTION")
    assert dtype == DecisionType.DENY
