from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.database.repositories.execution_repo import ExecutionRepository
from app.database.repositories.browser_repo import BrowserRepository
from app.engine.execution_engine import AgentExecutionEngine
from app.engine.task_graph import TaskGraph, TaskNode

router = APIRouter(prefix="/api/v1/research", tags=["Research"])


class StartResearchRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def start_research(
    req: StartResearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger controlled internet research workflow."""
    exec_repo = ExecutionRepository(db)
    execution = await exec_repo.create_execution(
        user_id=current_user.id,
        goal=f"Research: {req.query}",
        conversation_id=req.conversation_id
    )

    # Build research Task Graph: PLAN -> SEARCH -> BROWSE -> EXTRACT -> REVIEW
    graph = TaskGraph(execution.id, execution.goal)
    t_search = TaskNode(
        task_id=f"task_search_{execution.id[:8]}",
        goal=f"Search web sources for '{req.query}'",
        assigned_agent="browser"
    )
    t_review = TaskNode(
        task_id=f"task_review_{execution.id[:8]}",
        goal=f"Review research findings for '{req.query}'",
        assigned_agent="reviewer",
        dependencies=[t_search.id]
    )
    graph.add_task(t_search)
    graph.add_task(t_review)

    engine = AgentExecutionEngine(db=db)
    # Execute non-blocking or stream first step
    events = []
    async for evt in engine.run_execution(execution.id, graph, user_id=current_user.id):
        events.append(evt)
        if len(events) >= 5:
            break

    return {
        "execution_id": execution.id,
        "query": req.query,
        "status": "RUNNING",
        "initial_events": events
    }


@router.get("/{execution_id}")
async def get_research_status(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve research execution state and gathered sources."""
    exec_repo = ExecutionRepository(db)
    execution = await exec_repo.get_execution_by_id(execution_id)
    if not execution or execution.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research execution not found.")

    browser_repo = BrowserRepository(db)
    sources = await browser_repo.get_execution_sources(execution_id)

    return {
        "execution_id": execution.id,
        "goal": execution.goal,
        "status": execution.status,
        "created_at": execution.created_at.isoformat(),
        "sources": [
            {
                "source_id": s.source_id,
                "url": s.url,
                "title": s.title,
                "domain": s.domain,
                "summary": s.summary_json
            }
            for s in sources
        ]
    }
