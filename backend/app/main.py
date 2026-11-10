import json
import logging
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Depends, status
from starlette.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.config.logging import setup_logging, logger
from app.database.connection import get_db, AsyncSessionLocal
from app.database.repositories.conversation_repo import ConversationRepository
from app.database.repositories.user_repo import UserRepository
from app.security.authentication import get_password_hash
from app.database.migrations.run_migrations import run_migrations
from app.database.migrations.phase2_execution_engine import run_phase2_migration
from app.database.migrations.phase25_reliability import run_phase25_migration
from app.database.migrations.phase3_browser import run_phase3_migration
from app.database.migrations.phase4_code import run_phase4_migration
from app.database.migrations.phase5_perception import run_phase5_migrations
from app.database.migrations.phase6_intelligence import run_phase6_migrations
from app.database.migrations.phase7_workflows import run_phase7_migrations
from app.database.migrations.phase8_knowledge import run_phase8_migrations
from app.database.migrations.phase9_autonomy import run_phase9_migrations
from app.database.migrations.phase10_unified_runtime import run_phase10_migrations
from app.database.migrations.phase11_integrations import run_phase11_migrations
from app.core.ultron_core import UltronCore
from app.api.middleware.correlation import CorrelationIDMiddleware
from app.api.middleware.rate_limiter import ServerRateLimiterMiddleware
from app.api import auth, chat, memory, tasks, agents, tools, health, executions, browser, research, code, computer, perception, learning, workflows, knowledge, autonomy, ultron, integrations, metrics, feedback, ai

setup_logging()





@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI Application Lifespan Hook."""
    logger.info("Initializing ULTRON Backend Services & Phase 12 Production Infrastructure...")
    settings.validate_production_secrets()
    try:

        run_migrations()
        run_phase2_migration()
        run_phase25_migration()
        run_phase3_migration()
        run_phase4_migration()
        await run_phase5_migrations()
        await run_phase6_migrations()
        await run_phase7_migrations()
        await run_phase8_migrations()
        await run_phase9_migrations()
        await run_phase10_migrations()
        await run_phase11_migrations()
        # Ensure default local operator user is provisioned
        try:
            async with AsyncSessionLocal() as db_init:
                u_repo = UserRepository(db_init)
                op = await u_repo.get_by_username("ultron_user")
                if not op:
                    pwd_hash = get_password_hash("SecretPassword123")
                    await u_repo.create_user(username="ultron_user", email="user@ultron.ai", password_hash=pwd_hash)
                    logger.info("Default operator user 'ultron_user' auto-provisioned.")
        except Exception as ue:
            logger.debug("Operator init: %s", ue)
    except Exception as e:
        logger.warning("Database startup check: %s", e)
    yield
    logger.info("Shutting down ULTRON Backend Services...")


app = FastAPI(
    title="ULTRON Agentic AI Operating System API",
    version=settings.VERSION,
    description="Modular backend engine for ULTRON Agentic AI Operating System with Phase 12.8 Production Launch Control Center.",
    lifespan=lifespan
)

# Middleware
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(ServerRateLimiterMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()] if settings.CORS_ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(feedback.router)


app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(learning.router)
app.include_router(knowledge.router)
app.include_router(autonomy.router)
app.include_router(ultron.router)
app.include_router(integrations.router)
app.include_router(workflows.router)
app.include_router(ai.router)
app.include_router(tasks.router)
app.include_router(agents.router)

app.include_router(tools.router)
app.include_router(executions.router)
app.include_router(browser.router)

app.include_router(research.router)

app.include_router(code.router)
app.include_router(computer.router)

app.include_router(perception.router)







@app.websocket("/ws/chat/{conversation_id}")
@app.websocket("/api/v1/ws/chat/{conversation_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket Event Streaming Endpoint requiring JWT authentication or local operator fallback."""
    user_id: Optional[str] = None
    if token and token.strip() and token not in ("null", "undefined"):
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
        except JWTError:
            pass

    # Fallback to local operator if token is missing or unauthenticated on desktop
    if not user_id:
        user_repo = UserRepository(db)
        operator = await user_repo.get_by_username("ultron_user")
        if operator:
            user_id = operator.id
            logger.info("WebSocket auto-authenticated as default operator '%s'", user_id)
        else:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="JWT Authentication Failed")
            return

    # 2. Authorize Conversation Ownership
    conv_repo = ConversationRepository(db)
    conversation = await conv_repo.get_by_id(conversation_id)
    if not conversation:
        conversation = await conv_repo.create_conversation(user_id=user_id, title="Desktop Chat")
        conversation_id = conversation.id
    elif conversation.user_id != user_id:
        conversation = await conv_repo.create_conversation(user_id=user_id, title="Desktop Chat")
        conversation_id = conversation.id

    await websocket.accept()
    logger.info("WebSocket authenticated & authorized for conversation '%s', user '%s'", conversation_id, user_id)

    core = UltronCore(db=db)
    try:
        while True:
            data_text = await websocket.receive_text()
            try:
                payload_json = json.loads(data_text)
                user_input = (payload_json.get("message") or payload_json.get("content") or payload_json.get("text") or "").strip()
            except json.JSONDecodeError:
                user_input = data_text.strip()

            if not user_input:
                continue

            # Stream execution events
            try:
                async for event in core.process_message_stream(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    user_input=user_input
                ):
                    if websocket.client_state != WebSocketState.CONNECTED:
                        break
                    await websocket.send_json(event)
            except (WebSocketDisconnect, RuntimeError):
                logger.info("WebSocket disconnected during streaming for conversation '%s'", conversation_id)
                break

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for conversation '%s'", conversation_id)
    except Exception as e:
        logger.error("WebSocket exception: %s", e)
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
