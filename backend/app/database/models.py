import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
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
    browser_sessions = relationship("BrowserSessionModel", back_populates="user", cascade="all, delete-orphan")


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
    memory_type = Column(String(50), default="SEMANTIC", nullable=False, index=True)
    content = Column(Text, nullable=False)
    importance = Column(Integer, default=1, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    source = Column(String(255), default="user", nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    access_count = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="ACTIVE", nullable=False, index=True)
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
    browser_sessions = relationship("BrowserSessionModel", back_populates="execution")
    research_sources = relationship("ResearchSourceModel", back_populates="execution", cascade="all, delete-orphan")


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


# =========================================================================
# PHASE 3 ORM MODELS — Browser Architecture & Research
# =========================================================================

class BrowserSessionModel(Base):
    __tablename__ = "browser_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="SET NULL"), nullable=True, index=True)
    current_url = Column(String(2048), nullable=True)
    status = Column(String(50), default="ACTIVE", nullable=False, index=True)  # ACTIVE, CLOSED, ERROR
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="browser_sessions")
    execution = relationship("Execution", back_populates="browser_sessions")
    actions = relationship("BrowserActionModel", back_populates="session", cascade="all, delete-orphan")
    pages = relationship("BrowserPageModel", back_populates="session", cascade="all, delete-orphan")


class BrowserActionModel(Base):
    __tablename__ = "browser_actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("browser_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    params_json = Column(JSON, nullable=True)
    result_json = Column(JSON, nullable=True)
    status = Column(String(50), default="SUCCESS", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("BrowserSessionModel", back_populates="actions")


class BrowserPageModel(Base):
    __tablename__ = "browser_pages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("browser_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(String(2048), nullable=False)
    title = Column(String(512), nullable=True)
    page_structure_json = Column(JSON, nullable=True)
    captured_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("BrowserSessionModel", back_populates="pages")


class ResearchSourceModel(Base):
    __tablename__ = "research_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(100), nullable=False)
    url = Column(String(2048), nullable=False)
    title = Column(String(512), nullable=True)
    domain = Column(String(255), nullable=True, index=True)
    summary_json = Column(JSON, nullable=True)
    retrieved_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    execution = relationship("Execution", back_populates="research_sources")


# =========================================================================
# PHASE 4 ORM MODELS: CODE INTELLIGENCE & EXECUTION SANDBOX
# =========================================================================

class CodeWorkspaceModel(Base):
    __tablename__ = "code_workspaces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="SET NULL"), nullable=True, index=True)
    task_id = Column(String(36), nullable=True)
    name = Column(String(255), default="default_workspace", nullable=False)
    root_path = Column(String(1024), nullable=False)
    status = Column(String(50), default="ACTIVE", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    files = relationship("CodeFileModel", back_populates="workspace", cascade="all, delete-orphan")
    code_executions = relationship("CodeExecutionModel", back_populates="workspace", cascade="all, delete-orphan")


class CodeFileModel(Base):
    __tablename__ = "code_files"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("code_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    path = Column(String(1024), nullable=False)
    language = Column(String(50), default="text", nullable=False)
    content = Column(LongText if 'LongText' in globals() else Text, nullable=True)
    size_bytes = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    workspace = relationship("CodeWorkspaceModel", back_populates="files")


class CodeExecutionModel(Base):
    __tablename__ = "code_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("code_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(36), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent = Column(String(50), default="code_agent", nullable=False)
    runtime = Column(String(50), nullable=False)
    language = Column(String(50), nullable=False)
    status = Column(String(50), default="CREATED", nullable=False, index=True)
    exit_code = Column(Integer, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    cpu_usage_user_ms = Column(Integer, nullable=True)
    memory_usage_mb = Column(Integer, nullable=True)
    output_size_bytes = Column(Integer, nullable=True)
    artifact_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    workspace = relationship("CodeWorkspaceModel", back_populates="code_executions")
    events = relationship("CodeExecutionEventModel", back_populates="code_execution", cascade="all, delete-orphan")
    artifacts = relationship("CodeArtifactModel", back_populates="code_execution", cascade="all, delete-orphan")
    tests = relationship("CodeTestModel", back_populates="code_execution", cascade="all, delete-orphan")


class CodeExecutionEventModel(Base):
    __tablename__ = "code_execution_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code_execution_id = Column(String(36), ForeignKey("code_executions.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    code_execution = relationship("CodeExecutionModel", back_populates="events")


class CodeArtifactModel(Base):
    __tablename__ = "code_artifacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code_execution_id = Column(String(36), ForeignKey("code_executions.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(36), nullable=False)
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), default="text/plain", nullable=False)
    size_bytes = Column(Integer, default=0, nullable=False)
    hash_sha256 = Column(String(64), nullable=True)
    sandbox_path = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    code_execution = relationship("CodeExecutionModel", back_populates="artifacts")


class CodeTestModel(Base):
    __tablename__ = "code_tests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code_execution_id = Column(String(36), ForeignKey("code_executions.id", ondelete="CASCADE"), nullable=False, index=True)
    test_name = Column(String(255), nullable=False)
    framework = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    output = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    code_execution = relationship("CodeExecutionModel", back_populates="tests")


# =========================================================================
# PHASE 5 ORM MODELS — Perception Engine & Controlled Computer Interaction
# =========================================================================

class ComputerSessionModel(Base):
    __tablename__ = "computer_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="ACTIVE", nullable=False, index=True)
    viewport_width = Column(Integer, default=1280, nullable=False)
    viewport_height = Column(Integer, default=800, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    screenshots = relationship("ComputerScreenshotModel", back_populates="session", cascade="all, delete-orphan")
    actions = relationship("ComputerActionModel", back_populates="session", cascade="all, delete-orphan")


class ComputerScreenshotModel(Base):
    __tablename__ = "computer_screenshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("computer_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    image_metadata = Column(JSON, nullable=True)
    width = Column(Integer, default=1280, nullable=False)
    height = Column(Integer, default=800, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ComputerSessionModel", back_populates="screenshots")
    perception_results = relationship("PerceptionResultModel", back_populates="screenshot", cascade="all, delete-orphan")


class PerceptionResultModel(Base):
    __tablename__ = "perception_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    screenshot_id = Column(String(36), ForeignKey("computer_screenshots.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    result_json = Column(JSON, nullable=False)
    confidence = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    screenshot = relationship("ComputerScreenshotModel", back_populates="perception_results")


class ComputerActionModel(Base):
    __tablename__ = "computer_actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("computer_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False)
    target_json = Column(JSON, nullable=True)
    parameters_json = Column(JSON, nullable=True)
    status = Column(String(50), default="PENDING", nullable=False, index=True)
    approval_state = Column(String(50), default="AUTO_APPROVED", nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    result_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    session = relationship("ComputerSessionModel", back_populates="actions")


# =========================================================================
# PHASE 6 ORM MODELS — Intelligence, Memory, Learning & Strategy
# =========================================================================

class MemoryEmbeddingModel(Base):
    __tablename__ = "memory_embeddings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    memory_id = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True)
    vector_json = Column(JSON, nullable=False)
    dimension = Column(Integer, default=384, nullable=False)
    provider_name = Column(String(100), default="mock", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MemoryLinkModel(Base):
    __tablename__ = "memory_links"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_memory_id = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True)
    target_memory_id = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True)
    link_type = Column(String(50), default="related", nullable=False)
    strength = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MemoryVersionModel(Base):
    __tablename__ = "memory_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    memory_id = Column(String(36), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    content = Column(Text, nullable=False)
    importance = Column(Integer, default=1, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class EpisodicMemoryModel(Base):
    __tablename__ = "episodic_memories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    goal = Column(Text, nullable=False)
    plan_json = Column(JSON, nullable=True)
    agents_used_json = Column(JSON, nullable=True)
    tools_used_json = Column(JSON, nullable=True)
    execution_steps_json = Column(JSON, nullable=True)
    failures_json = Column(JSON, nullable=True)
    retries_count = Column(Integer, default=0, nullable=False)
    duration_ms = Column(Integer, default=0, nullable=False)
    final_result_json = Column(JSON, nullable=True)
    review_result_json = Column(JSON, nullable=True)
    success = Column(Boolean, default=True, nullable=False, index=True)
    lessons_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SemanticMemoryModel(Base):
    __tablename__ = "semantic_memories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(255), nullable=False, index=True)
    concept = Column(String(255), nullable=False)
    facts_json = Column(JSON, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    source = Column(String(255), default="consolidation", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ProceduralMemoryModel(Base):
    __tablename__ = "procedural_memories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    trigger_conditions_json = Column(JSON, nullable=True)
    steps_json = Column(JSON, nullable=False)
    agents_sequence_json = Column(JSON, nullable=True)
    tools_sequence_json = Column(JSON, nullable=True)
    success_rate = Column(Float, default=1.0, nullable=False)
    sample_count = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class PreferenceMemoryModel(Base):
    __tablename__ = "preference_memories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    source = Column(String(255), default="user_explicit", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class LearningEventModel(Base):
    __tablename__ = "learning_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    observation_json = Column(JSON, nullable=True)
    pattern_detected = Column(String(255), nullable=True)
    action_taken_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class StrategyLibraryModel(Base):
    __tablename__ = "strategy_library"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    goal_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    steps_json = Column(JSON, nullable=False)
    agents_json = Column(JSON, nullable=True)
    tools_json = Column(JSON, nullable=True)
    success_rate = Column(Float, default=1.0, nullable=False)
    sample_count = Column(Integer, default=1, nullable=False)
    average_duration_ms = Column(Integer, default=0, nullable=False)
    failure_rate = Column(Float, default=0.0, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class StrategyResultModel(Base):
    __tablename__ = "strategy_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    strategy_id = Column(String(36), ForeignKey("strategy_library.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    success = Column(Boolean, default=True, nullable=False)
    duration_ms = Column(Integer, default=0, nullable=False)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AgentMetricModel(Base):
    __tablename__ = "agent_metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    agent_name = Column(String(50), unique=True, nullable=False, index=True)
    total_runs = Column(Integer, default=0, nullable=False)
    successful_runs = Column(Integer, default=0, nullable=False)
    failed_runs = Column(Integer, default=0, nullable=False)
    average_duration_ms = Column(Integer, default=0, nullable=False)
    total_retries = Column(Integer, default=0, nullable=False)
    tools_usage_json = Column(JSON, nullable=True)
    average_review_score = Column(Float, default=1.0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ExecutionFeedbackModel(Base):
    __tablename__ = "execution_feedback"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, default=5, nullable=False)
    feedback_text = Column(Text, nullable=True)
    corrected_output_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# =========================================================================
# PHASE 7 ORM MODELS — Autonomous Orchestration & Workflow Engine
# =========================================================================

class WorkflowModel(Base):
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String(36), ForeignKey("executions.id", ondelete="SET NULL"), nullable=True, index=True)
    goal = Column(Text, nullable=False)
    strategy_id = Column(String(36), nullable=True)
    current_state = Column(String(32), default="CREATED", nullable=False, index=True)
    progress = Column(Float, default=0.0, nullable=False)
    current_step = Column(String(64), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    replan_count = Column(Integer, default=0, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    steps = relationship("WorkflowStepModel", back_populates="workflow", cascade="all, delete-orphan")
    events = relationship("WorkflowEventModel", back_populates="workflow", cascade="all, delete-orphan")
    checkpoints = relationship("WorkflowCheckpointModel", back_populates="workflow", cascade="all, delete-orphan")
    failures = relationship("WorkflowFailureModel", back_populates="workflow", cascade="all, delete-orphan")
    approvals = relationship("WorkflowApprovalModel", back_populates="workflow", cascade="all, delete-orphan")
    results = relationship("WorkflowResultModel", back_populates="workflow", cascade="all, delete-orphan")
    artifacts = relationship("WorkflowArtifactModel", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowStepModel(Base):
    __tablename__ = "workflow_steps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = Column(String(64), nullable=False)
    name = Column(String(255), nullable=False)
    assigned_agent = Column(String(64), nullable=False)
    status = Column(String(32), default="PENDING", nullable=False)
    dependencies_json = Column(JSON, nullable=True)
    input_data_json = Column(JSON, nullable=True)
    output_data_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    duration_ms = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    workflow = relationship("WorkflowModel", back_populates="steps")


class WorkflowEventModel(Base):
    __tablename__ = "workflow_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    workflow = relationship("WorkflowModel", back_populates="events")


class WorkflowCheckpointModel(Base):
    __tablename__ = "workflow_checkpoints"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    checkpoint_name = Column(String(128), nullable=False)
    state_snapshot_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    workflow = relationship("WorkflowModel", back_populates="checkpoints")


class WorkflowFailureModel(Base):
    __tablename__ = "workflow_failures"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(64), nullable=True)
    agent = Column(String(64), nullable=True)
    failure_type = Column(String(64), nullable=False)
    error_message = Column(Text, nullable=False)
    context_json = Column(JSON, nullable=True)
    recoverable = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    workflow = relationship("WorkflowModel", back_populates="failures")


class WorkflowApprovalModel(Base):
    __tablename__ = "workflow_approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(64), nullable=False)
    action_type = Column(String(64), nullable=False)
    details_json = Column(JSON, nullable=True)
    status = Column(String(32), default="PENDING", nullable=False)
    decided_by = Column(String(36), nullable=True)
    decided_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    workflow = relationship("WorkflowModel", back_populates="approvals")


class WorkflowResultModel(Base):
    __tablename__ = "workflow_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    status = Column(String(32), nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    evidence_json = Column(JSON, nullable=True)
    tasks_completed = Column(Integer, default=0, nullable=False)
    tasks_failed = Column(Integer, default=0, nullable=False)
    warnings_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    workflow = relationship("WorkflowModel", back_populates="results")


class WorkflowArtifactModel(Base):
    __tablename__ = "workflow_artifacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    artifact_type = Column(String(64), nullable=False)
    size_bytes = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    workflow = relationship("WorkflowModel", back_populates="artifacts")


# =========================================================================
# PHASE 8: MULTIMODAL KNOWLEDGE FABRIC & INTELLIGENT WORKSPACE MODELS
# =========================================================================

class KnowledgeWorkspaceModel(Base):
    __tablename__ = "knowledge_workspaces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    settings_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    sources = relationship("KnowledgeSourceModel", back_populates="workspace", cascade="all, delete-orphan")


class KnowledgeSourceModel(Base):
    __tablename__ = "knowledge_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("knowledge_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(64), nullable=False)
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(128), nullable=False)
    size_bytes = Column(Integer, default=0, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    origin = Column(String(255), nullable=False)
    status = Column(String(32), default="PENDING", nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    workspace = relationship("KnowledgeWorkspaceModel", back_populates="sources")
    documents = relationship("KnowledgeDocumentModel", back_populates="source", cascade="all, delete-orphan")
    chunks = relationship("KnowledgeChunkModel", back_populates="source", cascade="all, delete-orphan")
    citations = relationship("KnowledgeCitationModel", back_populates="source", cascade="all, delete-orphan")


class KnowledgeDocumentModel(Base):
    __tablename__ = "knowledge_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(36), ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    page_count = Column(Integer, default=1, nullable=False)
    language = Column(String(32), nullable=True)
    summary = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source = relationship("KnowledgeSourceModel", back_populates="documents")


class KnowledgeChunkModel(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(36), ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0, nullable=False)
    location_json = Column(JSON, nullable=True)
    checksum = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source = relationship("KnowledgeSourceModel", back_populates="chunks")
    embeddings = relationship("KnowledgeEmbeddingModel", back_populates="chunk", cascade="all, delete-orphan")


class KnowledgeEmbeddingModel(Base):
    __tablename__ = "knowledge_embeddings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    chunk_id = Column(String(36), ForeignKey("knowledge_chunks.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(36), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_name = Column(String(64), nullable=False)
    model_name = Column(String(64), nullable=False)
    dimension = Column(Integer, nullable=False)
    vector_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    chunk = relationship("KnowledgeChunkModel", back_populates="embeddings")


class KnowledgeEntityModel(Base):
    __tablename__ = "knowledge_entities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("knowledge_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    evidence_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class KnowledgeRelationshipModel(Base):
    __tablename__ = "knowledge_relationships"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("knowledge_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    source_entity_id = Column(String(36), nullable=False)
    target_entity_id = Column(String(36), nullable=False)
    relation_type = Column(String(64), nullable=False)
    provenance = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class KnowledgeCitationModel(Base):
    __tablename__ = "knowledge_citations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(36), ForeignKey("knowledge_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    citation_text = Column(Text, nullable=False)
    location_spec = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source = relationship("KnowledgeSourceModel", back_populates="citations")


class KnowledgeCollectionModel(Base):
    __tablename__ = "knowledge_collections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("knowledge_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class KnowledgeJobModel(Base):
    __tablename__ = "knowledge_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(36), nullable=False, index=True)
    job_type = Column(String(64), nullable=False)
    status = Column(String(32), default="PENDING", nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)


class KnowledgeArtifactModel(Base):
    __tablename__ = "knowledge_artifacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(36), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    artifact_type = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class KnowledgeAccessLogModel(Base):
    __tablename__ = "knowledge_access_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(36), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


# =========================================================================
# PHASE 9: PROACTIVE AUTONOMOUS AGENT & EVENT-DRIVEN INTELLIGENCE MODELS
# =========================================================================

class AutonomyRuleModel(Base):
    __tablename__ = "autonomy_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    trigger_type = Column(String(64), nullable=False)
    trigger_config_json = Column(JSON, nullable=True)
    goal_template = Column(Text, nullable=False)
    priority = Column(String(32), default="MEDIUM", nullable=False)
    autonomy_level = Column(String(32), default="LEVEL_1", nullable=False)
    cooldown_seconds = Column(Integer, default=300, nullable=False)
    max_runs_per_hour = Column(Integer, default=10, nullable=False)
    last_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AutonomyTriggerModel(Base):
    __tablename__ = "autonomy_triggers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    rule_id = Column(String(36), ForeignKey("autonomy_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    trigger_type = Column(String(64), nullable=False)
    source = Column(String(255), nullable=False)
    status = Column(String(32), default="ACTIVE", nullable=False)
    last_triggered_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    config_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AutonomyEventModel(Base):
    __tablename__ = "autonomy_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(String(36), nullable=True)
    event_type = Column(String(64), nullable=False)
    source = Column(String(255), nullable=False)
    payload_json = Column(JSON, nullable=True)
    importance = Column(String(32), default="MEDIUM", nullable=False)
    deduplication_key = Column(String(128), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AutonomyDecisionModel(Base):
    __tablename__ = "autonomy_decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_id = Column(String(36), ForeignKey("autonomy_events.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(String(36), nullable=True)
    decision_type = Column(String(64), nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    priority = Column(String(32), default="MEDIUM", nullable=False)
    reasoning = Column(Text, nullable=False)
    evidence_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AutonomyExecutionModel(Base):
    __tablename__ = "autonomy_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    rule_id = Column(String(36), ForeignKey("autonomy_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_id = Column(String(36), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(32), default="PENDING", nullable=False)
    result_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)


class AutonomyNotificationModel(Base):
    __tablename__ = "autonomy_notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(String(36), nullable=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    priority = Column(String(32), default="MEDIUM", nullable=False)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AutonomyMonitorStateModel(Base):
    __tablename__ = "autonomy_monitor_states"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_url_or_path = Column(String(2048), nullable=False)
    last_hash = Column(String(64), nullable=False)
    last_checked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    change_detected = Column(Boolean, default=False, nullable=False)
    metadata_json = Column(JSON, nullable=True)


class AutonomyPolicyOverrideModel(Base):
    __tablename__ = "autonomy_policy_overrides"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(String(36), ForeignKey("autonomy_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    override_level = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# =========================================================================
# PHASE 10: PERSONAL AGENT OPERATING SYSTEM & UNIFIED RUNTIME MODELS
# =========================================================================

class UltronCommandModel(Base):
    __tablename__ = "ultron_commands"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_id = Column(String(36), nullable=True, index=True)
    raw_message = Column(Text, nullable=False)
    intent_type = Column(String(64), nullable=False)
    status = Column(String(32), default="RECEIVED", nullable=False)
    result_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)


class UltronCapabilityModel(Base):
    __tablename__ = "ultron_capabilities"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(32), default="AVAILABLE", nullable=False)
    risk_level = Column(String(32), default="LOW", nullable=False)
    requires_approval = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class UltronProjectContextModel(Base):
    __tablename__ = "ultron_project_contexts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    workspace_id = Column(String(36), nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UltronResourceBudgetModel(Base):
    __tablename__ = "ultron_resource_budgets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_id = Column(String(36), nullable=False, index=True)
    max_tool_calls = Column(Integer, default=50, nullable=False)
    used_tool_calls = Column(Integer, default=0, nullable=False)
    max_runtime_seconds = Column(Integer, default=600, nullable=False)
    used_runtime_seconds = Column(Integer, default=0, nullable=False)
    max_browser_steps = Column(Integer, default=20, nullable=False)
    used_browser_steps = Column(Integer, default=0, nullable=False)
    status = Column(String(32), default="ACTIVE", nullable=False)


class UltronActivityTimelineModel(Base):
    __tablename__ = "ultron_activity_timeline"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_id = Column(String(36), nullable=True, index=True)
    activity_type = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    payload_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)








