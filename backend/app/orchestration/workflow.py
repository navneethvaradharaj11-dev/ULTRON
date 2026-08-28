from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.orchestration.workflow_state import WorkflowState

@dataclass
class WorkflowStep:
    step_id: str
    name: str
    assigned_agent: str
    status: str = "PENDING"
    dependencies: List[str] = field(default_factory=list)
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = 0
    duration_ms: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class WorkflowCheckpoint:
    id: str
    checkpoint_name: str
    state_snapshot: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class WorkflowFailure:
    id: str
    failure_type: str
    error_message: str
    task_id: Optional[str] = None
    agent: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    recoverable: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class WorkflowApproval:
    id: str
    task_id: str
    action_type: str
    details: Dict[str, Any] = field(default_factory=dict)
    status: str = "PENDING"
    decided_by: Optional[str] = None
    decided_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class WorkflowArtifact:
    id: str
    filename: str
    file_path: str
    artifact_type: str
    size_bytes: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class WorkflowResult:
    id: str
    workflow_id: str
    summary: str
    status: str
    confidence: float = 1.0
    evidence: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[WorkflowArtifact] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    tasks_completed: int = 0
    tasks_failed: int = 0
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Workflow:
    workflow_id: str
    user_id: str
    goal: str
    execution_id: Optional[str] = None
    strategy_id: Optional[str] = None
    current_state: WorkflowState = WorkflowState.CREATED
    progress: float = 0.0
    current_step: Optional[str] = None
    retry_count: int = 0
    replan_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    steps: List[WorkflowStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
