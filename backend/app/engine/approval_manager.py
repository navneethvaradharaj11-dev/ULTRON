import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.repositories.execution_repo import ExecutionRepository
from app.database.models import Approval

logger = logging.getLogger("ULTRON.ApprovalManager")


class ApprovalManager:
    """Manages backend-validated user approval requests for sensitive tool executions."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ExecutionRepository(db)

    async def create_request(
        self,
        execution_id: str,
        task_id: str,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Approval:
        logger.info("Creating pending approval request for execution='%s', tool='%s'", execution_id, tool_name)
        return await self.repo.create_approval_request(
            execution_id=execution_id,
            task_id=task_id,
            tool_name=tool_name,
            params_json=params
        )

    async def submit_response(self, approval_id: str, action: str) -> Optional[Approval]:
        """Process user decision ('approved' or 'denied')."""
        if action.lower() not in ["approved", "denied"]:
            raise ValueError(f"Invalid approval action '{action}'. Must be 'approved' or 'denied'.")
        
        logger.info("Updating approval '%s' to status '%s'", approval_id, action)
        return await self.repo.update_approval_status(approval_id, action.lower())
