import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database.connection import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    sessions = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    permissions = relationship("Permission", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    executions = relationship("Execution", back_populates="user", cascade="all, delete-orphan")


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="sessions")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), default="New Conversation", nullable=False)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="conversation")
    agent_runs = relationship("AgentRun", back_populates="conversation", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_type = Column(String(50), nullable=False)
    sender_name = Column(String(50), default="ULTRON", nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    memory_type = Column(String(50), default="long_term", nullable=False, index=True)
    content = Column(Text, nullable=False)
    importance = Column(Integer, default=1, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="memories")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending", nullable=False, index=True)
    priority = Column(String(20), default="medium", nullable=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="tasks")
    conversation = relationship("Conversation", back_populates="tasks")


class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    code_name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    capabilities_json = Column(JSON, nullable=True)
    status = Column(String(50), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    agent_runs = relationship("AgentRun", back_populates="agent")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="running", nullable=False)
    input_prompt = Column(Text, nullable=True)
    output_result = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    conversation = relationship("Conversation", back_populates="agent_runs")
    agent = relationship("AgentModel", back_populates="agent_runs")
    tool_calls = relationship("ToolCallModel", back_populates="agent_run", cascade="all, delete-orphan")


class ToolCallModel(Base):
    __tablename__ = "tool_calls"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    agent_run_id = Column(String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_name = Column(String(100), nullable=False, index=True)
    input_params_json = Column(JSON, nullable=True)
    output_result_json = Column(JSON, nullable=True)
    requires_approval = Column(Boolean, default=False, nullable=False)
    approval_status = Column(String(50), default="auto_approved", nullable=False)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    agent_run = relationship("AgentRun", back_populates="tool_calls")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    permission_level = Column(String(50), default="allow", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="permissions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    details_json = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="audit_logs")


# =========================================================================
# PHASE 2 ORM MODELS
# =========================================================================

class Execution(Base):
    __tablename__ = "executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    goal = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False, index=True)
    # Phase 2.5: Idempotency key — prevents duplicate executions from the same client request
    idempotency_key = Column(String(128), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="executions")
    conversation = relationship("Conversation", back_populates="executions")
    tasks = relationship("ExecutionTask", back_populates="execution", cascade="all, delete-orphan")
    events = relationship("ExecutionEvent", back_populates="execution", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="execution", cascade="all, delete-orphan")
    metrics = relationship("ExecutionMetrics", back_populates="execution", cascade="all, delete-orphan")


class ExecutionTask(Base):
    __tablename__ = "execution_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    goal = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_agent = Column(String(50), default="commander", nullable=False)
    dependencies_json = Column(JSON, nullable=True)
    status = Column(String(50), default="PENDING", nullable=False, index=True)
    priority = Column(String(20), default="medium", nullable=False)
    input_json = Column(JSON, nullable=True)
    output_json = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    execution = relationship("Execution", back_populates="tasks")
    approvals = relationship("Approval", back_populates="task", cascade="all, delete-orphan")


class ExecutionEvent(Base):
    __tablename__ = "execution_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    execution = relationship("Execution", back_populates="events")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(36), ForeignKey("execution_tasks.id", ondelete="CASCADE"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    params_json = Column(JSON, nullable=True)
    status = Column(String(50), default="pending", nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    execution = relationship("Execution", back_populates="approvals")
    task = relationship("ExecutionTask", back_populates="approvals")


# =========================================================================
# PHASE 2.5 ORM MODELS — Reliability & Evaluation
# =========================================================================

class ExecutionMetrics(Base):
    """Per-agent execution metrics collected after each agent task completes."""
    __tablename__ = "execution_metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(36), ForeignKey("execution_tasks.id", ondelete="CASCADE"), nullable=True)
    agent_name = Column(String(50), nullable=False, index=True)
    duration_ms = Column(Integer, default=0, nullable=False)
    status = Column(String(50), nullable=False)  # COMPLETED | FAILED
    retry_count = Column(Integer, default=0, nullable=False)
    tools_used_json = Column(JSON, nullable=True)  # list of tool names
    review_status = Column(String(50), nullable=True)  # approved | rejected | skipped
    review_confidence = Column(Integer, default=0, nullable=False)  # 0-100 integer
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    execution = relationship("Execution", back_populates="metrics")
