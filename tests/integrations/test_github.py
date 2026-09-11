import pytest
from app.integrations.github.adapter import GitHubAdapter


@pytest.mark.asyncio
async def test_github_adapter_read_operations():
    adapter = GitHubAdapter()
    repo = await adapter.execute("get_repository", {"owner": "navneethvaradharaj11-dev", "repo": "ULTRON"})
    assert repo["name"] == "ULTRON"

    issues = await adapter.execute("list_issues", {"owner": "navneethvaradharaj11-dev", "repo": "ULTRON"})
    assert len(issues) > 0


@pytest.mark.asyncio
async def test_github_adapter_merge_pr():
    adapter = GitHubAdapter()
    res = await adapter.execute("merge_pull_request", {"owner": "navneethvaradharaj11-dev", "repo": "ULTRON", "number": 50})
    assert res["merged"] is True
