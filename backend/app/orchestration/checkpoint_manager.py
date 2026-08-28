import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.repositories.workflow_repo import WorkflowRepository

logger = logging.getLogger(__name__)

class CheckpointManager:
    """Checkpoint Manager handling state snapshot serialization and crash recovery."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WorkflowRepository(db)

    async def save_checkpoint(
        self,
        workflow_id: str,
        checkpoint_name: str,
        state_snapshot: Dict[str, Any]
    ) -> Any:
        """Persist a workflow execution checkpoint."""
        logger.info("Saving checkpoint '%s' for workflow '%s'", checkpoint_name, workflow_id)
        return await self.repo.create_checkpoint(
            workflow_id=workflow_id,
            checkpoint_name=checkpoint_name,
            state_snapshot=state_snapshot
        )

    async def load_latest_checkpoint(
        self,
        workflow_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve the latest valid checkpoint snapshot for crash recovery."""
        cp = await self.repo.get_latest_checkpoint(workflow_id, user_id)
        if not cp:
            return None
        return cp.state_snapshot_json
