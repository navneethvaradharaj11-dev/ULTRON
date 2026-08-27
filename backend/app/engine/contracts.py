from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"


class AgentExecutionResult(BaseModel):
    """Structured contract returned by every agent execution."""
    execution_id: str
    agent_name: str
    task_id: str
    status: TaskStatus
    input: Dict[str, Any] = Field(default_factory=dict)
    output: Dict[str, Any] = Field(default_factory=dict)
    tools_used: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    duration_ms: int = 0
    next_action: Optional[str] = None


class ReviewResult(BaseModel):
    """Structured contract returned by Reviewer Agent."""
    status: str  # "approved" or "rejected"
    issues: List[str] = Field(default_factory=list)
    confidence: float = 1.0
