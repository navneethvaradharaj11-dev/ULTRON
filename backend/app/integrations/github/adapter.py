import logging
from typing import Dict, Any
from app.integrations.contracts import IntegrationDescriptor, OperationDescriptor
from app.integrations.integration_registry import integration_registry
from app.integrations.github.client import GitHubClient

logger = logging.getLogger("ULTRON.Integrations.GitHubAdapter")


class GitHubAdapter:
    """GitHub Service Adapter wrapping read/write operations with policy metadata."""

    INTEGRATION_ID = "github"

    def __init__(self, client: Optional[GitHubClient] = None):
        self.client = client or GitHubClient()
        self._register_descriptor()

    def _register_descriptor(self):
        desc = IntegrationDescriptor(
            id=self.INTEGRATION_ID,
            name="GitHub",
            version="1.0.0",
            provider="GitHub",
            description="GitHub Repository, Issues, Pull Requests & Webhook Integration",
            capabilities=["code", "workflows", "knowledge"],
            risk_level="MEDIUM",
            authentication_type="OAUTH2",
            required_scopes=["READ_REPOSITORY", "READ_ISSUES", "CREATE_ISSUE", "CREATE_PULL_REQUEST", "MERGE_PULL_REQUEST"],
            supported_operations={
                "get_repository": OperationDescriptor(
                    operation_id="get_repository",
                    description="Get repository details",
                    risk_level="LOW",
                    requires_approval=False,
                    required_scopes=["READ_REPOSITORY"]
                ),
                "list_issues": OperationDescriptor(
                    operation_id="list_issues",
                    description="List repository issues",
                    risk_level="LOW",
                    requires_approval=False,
                    required_scopes=["READ_ISSUES"]
                ),
                "create_issue": OperationDescriptor(
                    operation_id="create_issue",
                    description="Create a new GitHub issue",
                    risk_level="MEDIUM",
                    requires_approval=False,
                    required_scopes=["CREATE_ISSUE"]
                ),
                "create_pull_request": OperationDescriptor(
                    operation_id="create_pull_request",
                    description="Create a pull request",
                    risk_level="MEDIUM",
                    requires_approval=False,
                    required_scopes=["CREATE_PULL_REQUEST"]
                ),
                "merge_pull_request": OperationDescriptor(
                    operation_id="merge_pull_request",
                    description="Merge a pull request into target branch",
                    risk_level="HIGH",
                    requires_approval=True,
                    required_scopes=["MERGE_PULL_REQUEST"]
                )
            }
        )
        integration_registry.register(desc)

    async def execute(self, operation_id: str, parameters: Dict[str, Any]) -> Any:
        op = operation_id.lower()
        owner = parameters.get("owner", "navneethvaradharaj11-dev")
        repo = parameters.get("repo", "ULTRON")

        if op == "get_repository":
            return await self.client.get_repository(owner, repo)
        elif op == "list_issues":
            return await self.client.list_issues(owner, repo)
        elif op == "create_issue":
            return await self.client.create_issue(owner, repo, parameters.get("title", "New Issue"), parameters.get("body"))
        elif op == "create_pull_request":
            return await self.client.create_pull_request(owner, repo, parameters.get("title", "New PR"), parameters.get("head", "feature"), parameters.get("base", "main"))
        elif op == "merge_pull_request":
            return await self.client.merge_pull_request(owner, repo, int(parameters.get("number", 1)))
        else:
            raise ValueError(f"Unsupported GitHub operation '{op}'")
