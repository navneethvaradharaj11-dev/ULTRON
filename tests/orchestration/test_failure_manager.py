from app.orchestration.failure_manager import FailureManager

def test_failure_manager_classification_and_sanitization():
    # Timeout classification
    res1 = FailureManager.classify_failure("Browser navigation timeout after 30s")
    assert res1["failure_type"] == "TIMEOUT"
    assert res1["recoverable"] is True

    # Security classification
    res2 = FailureManager.classify_failure("Security error: Unauthorized access to system")
    assert res2["failure_type"] == "SECURITY_FAILURE"
    assert res2["recoverable"] is False

    # Secret redaction in error message
    res3 = FailureManager.classify_failure("Failed connection api_key: 'sk_live_12345678901234567890'")
    assert "sk_live_" not in res3["error_message"]
    assert "[REDACTED" in res3["error_message"]
