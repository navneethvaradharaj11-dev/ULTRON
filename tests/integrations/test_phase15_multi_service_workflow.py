import pytest
from app.integrations.contracts import IntegrationExecutionRequest
from app.integrations.integration_manager import IntegrationManager
from app.integrations.github.adapter import GitHubAdapter
from app.integrations.calendar.adapter import CalendarAdapter
from app.integrations.email.adapter import EmailAdapter
from app.integrations.filesystem.adapter import FilesystemAdapter
from app.integrations.health_manager import health_manager
from app.integrations.rate_limiter import integration_rate_limiter


@pytest.fixture
def multi_service_manager():
    manager = IntegrationManager(adapters={
        "github": GitHubAdapter(),
        "calendar": CalendarAdapter(),
        "email": EmailAdapter(),
        "filesystem": FilesystemAdapter()
    })
    return manager


@pytest.mark.asyncio
async def test_1_github_real_world_execution(multi_service_manager):
    req = IntegrationExecutionRequest(
        user_id="phase15_tester",
        integration_id="github",
        operation_id="get_repository",
        parameters={"owner": "navneethvaradharaj11-dev", "repo": "ULTRON"}
    )
    res = await multi_service_manager.execute_operation(req)
    assert res.status == "SUCCESS"
    assert res.result is not None
    assert "name" in res.result or "full_name" in res.result or "description" in res.result


@pytest.mark.asyncio
async def test_2_calendar_event_scheduling(multi_service_manager):
    req = IntegrationExecutionRequest(
        user_id="phase15_tester",
        integration_id="calendar",
        operation_id="create_event",
        parameters={
            "summary": "ULTRON Phase 15 Integration Review",
            "start_time": "2026-11-08T10:00:00Z",
            "end_time": "2026-11-08T11:00:00Z"
        }
    )
    res = await multi_service_manager.execute_operation(req)
    assert res.status in ["SUCCESS", "APPROVAL_REQUIRED"]


@pytest.mark.asyncio
async def test_3_email_notification_dispatch(multi_service_manager):
    req = IntegrationExecutionRequest(
        user_id="phase15_tester",
        integration_id="email",
        operation_id="create_draft",
        parameters={
            "to": "operator@ultron.internal",
            "subject": "ULTRON System Health Alert",
            "body": "All 16 capabilities active."
        }
    )
    res = await multi_service_manager.execute_operation(req)
    assert res.status in ["SUCCESS", "APPROVAL_REQUIRED"]


@pytest.mark.asyncio
async def test_4_multi_service_composite_pipeline(multi_service_manager):
    user = "pipeline_operator"

    # Step 1: Fetch GitHub repo info
    git_req = IntegrationExecutionRequest(
        user_id=user,
        integration_id="github",
        operation_id="get_repository",
        parameters={"owner": "navneethvaradharaj11-dev", "repo": "ULTRON"}
    )
    git_res = await multi_service_manager.execute_operation(git_req)
    assert git_res.status == "SUCCESS"

    # Step 2: Write audit log to filesystem
    fs_req = IntegrationExecutionRequest(
        user_id=user,
        integration_id="filesystem",
        operation_id="write_file",
        parameters={
            "path": "sandbox/artifacts/phase15_audit.log",
            "content": f"Repository verified: {git_res.result.get('full_name', 'ULTRON')}"
        }
    )
    fs_res = await multi_service_manager.execute_operation(fs_req)
    assert fs_res.status in ["SUCCESS", "APPROVAL_REQUIRED"]

    # Step 3: Check integration health registry
    status = health_manager.get_status("github")
    assert status in ["HEALTHY", "CONNECTED", "DEGRADED", "READY"]
