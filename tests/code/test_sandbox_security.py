import os
import pytest
from app.sandbox.resource_limits import ResourceLimits
from app.sandbox.network_policy import NetworkPolicy, NetworkPolicyMode
from app.sandbox.sandbox_policy import SandboxPolicy, SandboxActionRisk
from app.sandbox.filesystem import SandboxFilesystem
from app.sandbox.process_manager import ProcessManager
from app.sandbox.sandbox_manager import SandboxManager, SandboxUnavailableError


def test_filesystem_escape_prevented(tmp_path):
    fs = SandboxFilesystem("sec_exec_1", base_dir=str(tmp_path))
    with pytest.raises(ValueError, match="ACCESS_DENIED"):
        fs.resolve_path("../../etc/passwd")

    with pytest.raises(ValueError, match="ACCESS_DENIED"):
        fs.resolve_path("C:\\Windows\\System32")


def test_path_traversal_policy_forbidden():
    risk, reason = SandboxPolicy.evaluate_action("READ_FILE", path="../.env")
    assert risk == SandboxActionRisk.FORBIDDEN
    assert "ACCESS_DENIED" in reason


def test_access_to_env_file_forbidden():
    risk, reason = SandboxPolicy.evaluate_action("READ_FILE", path=".env")
    assert risk == SandboxActionRisk.FORBIDDEN
    assert "ACCESS_DENIED" in reason


def test_access_to_ultron_source_forbidden():
    risk, reason = SandboxPolicy.evaluate_action("READ_FILE", path="backend/app/main.py")
    assert risk == SandboxActionRisk.FORBIDDEN


def test_env_variable_leakage_prevented(tmp_path):
    pm = ProcessManager()
    os.environ["SECRET_JWT_KEY"] = "super_secret_test_key"
    res = pm.run_command(["python", "-c", "import os; print(os.environ.get('SECRET_JWT_KEY', ''))"], cwd=str(tmp_path))
    assert "super_secret_test_key" not in res.stdout


def test_infinite_loop_timeout(tmp_path):
    limits = ResourceLimits(timeout_seconds=1.0)
    pm = ProcessManager(limits=limits)
    res = pm.run_command(["python", "-c", "while True: pass"], cwd=str(tmp_path))
    assert res.status == "TIMEOUT"
    assert "TIMEOUT" in res.stderr


def test_output_flooding_truncated(tmp_path):
    limits = ResourceLimits(max_output_bytes=100)
    pm = ProcessManager(limits=limits)
    res = pm.run_command(["python", "-c", "print('A' * 10000)"], cwd=str(tmp_path))
    assert res.status == "OUTPUT_LIMIT_EXCEEDED"
    assert "TRUNCATED" in res.stdout


def test_excessive_file_creation_prevented(tmp_path):
    limits = ResourceLimits(max_files=2)
    fs = SandboxFilesystem("sec_exec_files", base_dir=str(tmp_path), limits=limits)
    fs.write_file("file1.txt", "a")
    fs.write_file("file2.txt", "b")
    with pytest.raises(ValueError, match="FILE_LIMIT_EXCEEDED"):
        fs.write_file("file3.txt", "c")


def test_network_access_denial_deny_all():
    np = NetworkPolicy(mode=NetworkPolicyMode.DENY_ALL)
    allowed, reason = np.validate_destination("https://api.github.com")
    assert not allowed
    assert "NETWORK_DENIED" in reason


def test_localhost_access_denial():
    np = NetworkPolicy(mode=NetworkPolicyMode.APPROVED_DOMAINS, allowed_domains=["*"])
    for target in ["127.0.0.1", "localhost", "127.0.0.5"]:
        allowed, reason = np.validate_destination(target)
        assert not allowed
        assert "NETWORK_DENIED" in reason


def test_private_ip_access_denial():
    np = NetworkPolicy(mode=NetworkPolicyMode.APPROVED_DOMAINS, allowed_domains=["*"])
    for target in ["10.0.0.1", "192.168.1.1", "172.16.0.1"]:
        allowed, reason = np.validate_destination(target)
        assert not allowed
        assert "NETWORK_DENIED" in reason


def test_metadata_endpoint_denial():
    np = NetworkPolicy(mode=NetworkPolicyMode.APPROVED_DOMAINS, allowed_domains=["*"])
    for target in ["169.254.169.254", "http://metadata.google.internal"]:
        allowed, reason = np.validate_destination(target)
        assert not allowed
        assert "NETWORK_DENIED" in reason


def test_cross_user_workspace_access_denied():
    sm = SandboxManager()
    sm.get_or_create_session(execution_id="exec_100", task_id="t1", user_id="user_a")
    with pytest.raises(PermissionError, match="ACCESS_DENIED"):
        sm.get_session(execution_id="exec_100", task_id="t1", user_id="user_b")


def test_cross_execution_workspace_access_denied():
    sm = SandboxManager()
    s1 = sm.get_or_create_session(execution_id="exec_A", task_id="t1", user_id="user_a")
    s2 = sm.get_or_create_session(execution_id="exec_B", task_id="t1", user_id="user_a")
    assert s1.filesystem.sandbox_dir != s2.filesystem.sandbox_dir


def test_cancellation():
    sm = SandboxManager()
    sess = sm.get_or_create_session(execution_id="exec_cancel", task_id="t1", user_id="user_a")
    sm.destroy_session(execution_id="exec_cancel", task_id="t1", user_id="user_a")
    assert not sess.active


def test_approval_bypass_attempt_forbidden():
    risk, reason = SandboxPolicy.evaluate_action("PRIVILEGED_OP")
    assert risk == SandboxActionRisk.REQUIRES_APPROVAL
