import pytest
from app.integrations.contracts import IntegrationExecutionRequest
from app.integrations.integration_manager import IntegrationManager
from app.integrations.github.adapter import GitHubAdapter


@pytest.mark.asyncio
async def test_integration_manager_execution_pipeline():
    github_adapter = GitHubAdapter()
    manager = IntegrationManager(adapters={"github": github_adapter})

    req = IntegrationExecutionRequest(
        user_id="user_test",
        integration_id="github",
        operation_id="get_repository",
        parameters={"owner": "navneethvaradharaj11-dev", "repo": "ULTRON"}
    )

    res = await manager.execute_operation(req)
    assert res.status == "SUCCESS"
    assert res.result is not None
