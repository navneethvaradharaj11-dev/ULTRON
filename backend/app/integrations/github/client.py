import logging
from typing import Dict, Any, List, Optional
from app.integrations.github.models import RepositoryModel, IssueModel, PullRequestModel

logger = logging.getLogger("ULTRON.Integrations.GitHubClient")


class GitHubClient:
    """Mock/Real client for GitHub API interaction."""

    def __init__(self, token: Optional[str] = None):
        self.token = token

    def _to_dict(self, model_obj: Any) -> Dict[str, Any]:
        return model_obj.model_dump() if hasattr(model_obj, "model_dump") else model_obj.dict()

    async def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        return self._to_dict(RepositoryModel(
            id=f"{owner}/{repo}",
            name=repo,
            owner=owner,
            description=f"GitHub repository {owner}/{repo}",
            default_branch="main"
        ))

    async def list_issues(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        return [
            self._to_dict(IssueModel(id="issue_101", number=101, title="Fix security bounds check", body="High priority security issue", author="alice")),
            self._to_dict(IssueModel(id="issue_102", number=102, title="Add feature documentation", body="Update Phase 11 docs", author="bob"))
        ]

    async def get_issue(self, owner: str, repo: str, number: int) -> Dict[str, Any]:
        return self._to_dict(IssueModel(id=f"issue_{number}", number=number, title=f"Issue #{number}", body="Detailed description", author="alice"))

    async def list_pull_requests(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        return [
            self._to_dict(PullRequestModel(id="pr_50", number=50, title="Phase 11 Integrations", body="Implement GitHub adapter", head_branch="phase11-integrations", base_branch="main"))
        ]

    async def create_issue(self, owner: str, repo: str, title: str, body: Optional[str] = None) -> Dict[str, Any]:
        return self._to_dict(IssueModel(id="issue_103", number=103, title=title, body=body or "", author="ULTRON"))

    async def create_pull_request(self, owner: str, repo: str, title: str, head: str, base: str) -> Dict[str, Any]:
        return self._to_dict(PullRequestModel(id="pr_51", number=51, title=title, head_branch=head, base_branch=base))

    async def merge_pull_request(self, owner: str, repo: str, number: int) -> Dict[str, Any]:
        return {"merged": True, "message": f"Pull Request #{number} merged successfully."}

