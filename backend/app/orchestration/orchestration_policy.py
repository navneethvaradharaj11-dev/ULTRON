from pydantic import BaseModel, Field

class OrchestrationPolicy(BaseModel):
    max_workflow_tasks: int = Field(default=50, description="Maximum total steps/tasks in a workflow")
    max_workflow_duration_seconds: int = Field(default=300, description="Maximum workflow execution time in seconds")
    max_workflow_retries: int = Field(default=3, description="Maximum total retries across steps")
    max_replans: int = Field(default=3, description="Maximum dynamic re-plans allowed")
    max_concurrent_agents: int = Field(default=5, description="Maximum concurrent agent executions")

default_orchestration_policy = OrchestrationPolicy()
