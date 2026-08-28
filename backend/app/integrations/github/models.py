from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RepositoryModel(BaseModel):
    id: str
    name: str
    owner: str
    description: Optional[str] = None
    default_branch: str = "main"


class IssueModel(BaseModel):
    id: str
    number: int
    title: str
    body: Optional[str] = None
    state: str = "open"
    author: str


class PullRequestModel(BaseModel):
    id: str
    number: int
    title: str
    body: Optional[str] = None
    state: str = "open"
    head_branch: str
    base_branch: str
