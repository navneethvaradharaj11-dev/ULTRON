from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class AutonomyLevel(str, Enum):
    LEVEL_0 = "LEVEL_0"  # OBSERVE_ONLY
    LEVEL_1 = "LEVEL_1"  # NOTIFY_ONLY
    LEVEL_2 = "LEVEL_2"  # LOW_RISK_AUTONOMOUS_ACTION
    LEVEL_3 = "LEVEL_3"  # APPROVAL_REQUIRED
    LEVEL_4 = "LEVEL_4"  # FORBIDDEN


class TriggerType(str, Enum):
    SCHEDULE = "SCHEDULE"
    INTERVAL = "INTERVAL"
    WEB_CHANGE = "WEB_CHANGE"
    WORKFLOW_EVENT = "WORKFLOW_EVENT"
    KNOWLEDGE_UPDATE = "KNOWLEDGE_UPDATE"
    FILE_CHANGE = "FILE_CHANGE"
    MANUAL = "MANUAL"
    SYSTEM_EVENT = "SYSTEM_EVENT"


class PriorityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class DecisionType(str, Enum):
    IGNORE = "IGNORE"
    NOTIFY = "NOTIFY"
    ASK_USER = "ASK_USER"
    START_WORKFLOW = "START_WORKFLOW"
    RUN_AUTONOMOUSLY = "RUN_AUTONOMOUSLY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DENY = "DENY"


class AutonomyEventPayload(BaseModel):
    event_id: str
    user_id: str
    event_type: str
    source: str
    deduplication_key: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    importance: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    timestamp: str


class AutonomyDecisionPayload(BaseModel):
    decision_id: str
    event_id: str
    user_id: str
    rule_id: Optional[str] = None
    decision_type: DecisionType
    confidence: float = 1.0
    priority: PriorityLevel = PriorityLevel.MEDIUM
    reasoning: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
