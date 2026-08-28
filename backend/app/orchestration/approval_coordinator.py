import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.engine.approval_manager import ApprovalManager
from app.database.repositories.workflow_repo import WorkflowRepository

logger = logging.getLogger(__name__)

class ApprovalCoordinator:
    """Approval Coordinator managing human-in-the-loop approvals for sensitive workflow actions."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.approval_mgr = ApprovalManager(db)
        self.repo = WorkflowRepository(db)

    async def request_approval(
        self,
        workflow_id: str,
        execution_id: str,
        task_id: str,
        action_type: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create backend approval request and transition workflow state."""
        appr_obj = await self.approval_mgr.create_approval_request(
            execution_id=execution_id,
            task_id=task_id,
            tool_name=action_type,
            params=details or {}
        )
        await self.repo.create_approval(
            workflow_id=workflow_id,
            task_id=task_id,
            action_type=action_type,
            details=details or {}
        )
        return {
            "approval_id": appr_obj.id,
            "status": "WAITING_APPROVAL",
            "task_id": task_id,
            "action_type": action_type
        }

    async def process_approval_decision(
        self,
        workflow_id: str,
        approval_id: str,
        user_id: str,
        approved: bool
    ) -> Dict[str, Any]:
        """Process user decision server-side."""
        status = "APPROVED" if approved else "DENIED"
        appr = await self.repo.update_approval(
            workflow_id=workflow_id,
            approval_id=approval_id,
            user_id=user_id,
            status=status
        )
        if not appr:
            raise ValueError("Approval request not found or access denied")

        return {
            "workflow_id": workflow_id,
            "approval_id": approval_id,
            "status": status
        }
