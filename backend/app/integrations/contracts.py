import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger("ULTRON.Integrations.Contracts")


class OperationDescriptor(BaseModel):
    operation_id: str
    description: str
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    requires_approval: bool = False
    required_scopes: List[str] = Field(default_factory=list)
    resource_cost: int = 1
    timeout_seconds: int = 30


class IntegrationDescriptor(BaseModel):
    id: str
    name: str
    version: str = "1.0.0"
    provider: str
    description: str
    capabilities: List[str] = Field(default_factory=list)
    risk_level: str = "LOW"
    authentication_type: str = "OAUTH2"  # OAUTH2, API_KEY, NONE
    required_scopes: List[str] = Field(default_factory=list)
    supported_operations: Dict[str, OperationDescriptor] = Field(default_factory=dict)
    health_status: str = "CONNECTED"  # CONNECTED, DISCONNECTED, AUTH_REQUIRED, RATE_LIMITED, DEGRADED


class IntegrationCredential(BaseModel):
    integration_id: str
    user_id: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    api_key: Optional[str] = None
    expires_at: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class IntegrationExecutionRequest(BaseModel):
    user_id: str
    integration_id: str
    operation_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    workflow_id: Optional[str] = None


class IntegrationExecutionResponse(BaseModel):
    status: str  # SUCCESS, FAILED, REQUIRES_APPROVAL, RATE_LIMITED
    result: Optional[Any] = None
    error_message: Optional[str] = None
    duration_ms: int = 0

