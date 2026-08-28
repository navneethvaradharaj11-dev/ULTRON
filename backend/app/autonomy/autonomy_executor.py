import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestration.orchestrator import WorkflowOrchestrator
from app.autonomy.notification_engine import NotificationEngine
from app.autonomy.contracts import DecisionType, AutonomyDecisionPayload

logger = logging.getLogger("ULTRON.AutonomyExecutor")


class AutonomyExecutor:
    """Executes decision actions by dispatching workflows through Phase 7 WorkflowOrchestrator."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.orchestrator = WorkflowOrchestrator(db)
        self.notification_engine = NotificationEngine(db)

    async def execute_decision(
        self,
        decision: AutonomyDecisionPayload,
        goal_template: str,
        rule_id: Optional[str] = None
    ) -> Dict[str, Any]:
        user_id = decision.user_id
        dtype = decision.decision_type

        if dtype == DecisionType.NOTIFY:
            notif = await self.notification_engine.send_notification(
                user_id=user_id,
                title=f"Proactive Alert: {decision.priority.value}",
                summary=decision.reasoning,
                priority=decision.priority.value,
                rule_id=rule_id
            )
            return {"action": "NOTIFY", "notification_id": notif["notification_id"]}

        elif dtype in (DecisionType.START_WORKFLOW, DecisionType.RUN_AUTONOMOUSLY):
            # Create normal Phase 7 workflow
            goal = goal_template or "Proactive autonomous execution"
            wf = await self.orchestrator.create_workflow(user_id=user_id, goal=goal)
            
            # Start background workflow execution
            events = []
            async for evt in self.orchestrator.execute_workflow(wf.workflow_id, user_id):
                events.append(evt)

            await self.notification_engine.send_notification(
                user_id=user_id,
                title=f"Autonomous Workflow Completed: {wf.workflow_id[:8]}",
                summary=f"Goal: {goal} completed with status: {wf.current_state.value}",
                priority=decision.priority.value,
                rule_id=rule_id
            )

            return {
                "action": "WORKFLOW_EXECUTED",
                "workflow_id": wf.workflow_id,
                "status": wf.current_state.value,
                "events_count": len(events)
            }

        elif dtype == DecisionType.REQUIRE_APPROVAL:
            notif = await self.notification_engine.send_notification(
                user_id=user_id,
                title="Approval Required for Autonomous Action",
                summary=f"Action requires approval: {decision.reasoning}",
                priority="HIGH",
                rule_id=rule_id
            )
            return {"action": "REQUIRE_APPROVAL", "notification_id": notif["notification_id"]}

        else:
            return {"action": "IGNORED", "reason": decision.reasoning}
