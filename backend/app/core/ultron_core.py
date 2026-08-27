import re
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config.settings import settings
from app.ai.model_manager import ModelManager
from app.ai.context import ContextBuilder
from app.memory.memory_manager import MemoryManager
from app.agents.orchestrator import AgentOrchestrator
from app.tools.registry import default_tool_registry
from app.database.models import AgentModel, AgentRun, ToolCallModel

logger = logging.getLogger("ULTRON.Core")


class UltronCore:
    """Central ULTRON Core engine managing context, memory, tools, and agent execution with database observability."""

    def __init__(self, db: AsyncSession, model_manager: Optional[ModelManager] = None):
        self.db = db
        self.model_manager = model_manager or ModelManager()
        self.context_builder = ContextBuilder(max_history_messages=settings.MAX_CONTEXT_MESSAGES)
        self.memory_manager = MemoryManager(db)
        self.orchestrator = AgentOrchestrator(self.model_manager)
        self.tool_registry = default_tool_registry

    async def process_message_stream(
        self,
        conversation_id: str,
        user_id: str,
        user_input: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream structured WebSocket events for agent execution lifecycle and record agent runs in MySQL."""
        yield {"type": "message_start", "conversation_id": conversation_id}

        # Save user message to database conversation memory
        await self.memory_manager.save_message(
            conversation_id=conversation_id,
            sender_type="user",
            sender_name="User",
            content=user_input
        )

        # Retrieve Commander agent database ID
        agent_stmt = select(AgentModel).where(AgentModel.code_name == "commander")
        res = await self.db.execute(agent_stmt)
        commander_agent = res.scalars().first()
        agent_id = commander_agent.id if commander_agent else "agent-commander-001"

        # Record Agent Run in database
        agent_run = AgentRun(
            conversation_id=conversation_id,
            agent_id=agent_id,
            status="running",
            input_prompt=user_input,
            created_at=datetime.utcnow()
        )
        self.db.add(agent_run)
        await self.db.commit()
        await self.db.refresh(agent_run)

        # Event: agent_started
        yield {"type": "agent_started", "agent": "commander", "run_id": agent_run.id, "status": "Analyzing request and context..."}

        # Build Context with history & long-term memories
        history = await self.memory_manager.get_conversation_history(conversation_id, limit=settings.MAX_CONTEXT_MESSAGES)
        memories = await self.memory_manager.get_long_term_memories(user_id)
        context_prompt = self.context_builder.build_prompt_with_context(user_input, history, memories)

        # Check for tool execution triggers
        tool_call_match = self._detect_tool_intent(user_input)
        if tool_call_match:
            tool_name, tool_params = tool_call_match
            yield {"type": "agent_progress", "agent": "commander", "detail": f"Routing to tool '{tool_name}'"}
            yield {"type": "tool_started", "tool_name": tool_name, "params": tool_params}

            # Execute tool
            tool_res = await self.tool_registry.execute_tool(
                name=tool_name,
                params=tool_params,
                user_id=user_id,
                db=self.db
            )

            # Record Tool Call in database
            tool_call_rec = ToolCallModel(
                agent_run_id=agent_run.id,
                tool_name=tool_name,
                input_params_json=tool_params,
                output_result_json=tool_res,
                requires_approval=tool_res.get("requires_approval", False),
                approval_status="pending_approval" if tool_res.get("requires_approval") else ("approved" if tool_res.get("success") else "denied"),
                execution_time_ms=tool_res.get("execution_time_ms", 0)
            )
            self.db.add(tool_call_rec)
            await self.db.commit()

            if tool_res.get("requires_approval"):
                yield {
                    "type": "approval_required",
                    "tool_name": tool_name,
                    "params": tool_params,
                    "message": tool_res.get("message")
                }
                agent_run.status = "blocked"
                await self.db.commit()
                return

            yield {
                "type": "tool_completed",
                "tool_name": tool_name,
                "result": tool_res.get("result", tool_res.get("error")),
                "execution_time_ms": tool_res.get("execution_time_ms", 0)
            }

            # Synthesize final response with tool result
            tool_output_str = str(tool_res.get("result", tool_res.get("error")))
            synthesis_prompt = f"User asked: {user_input}\nTool '{tool_name}' produced: {tool_output_str}\nSummarize the answer clearly."
            
            full_response = ""
            async for chunk in self.model_manager.stream(synthesis_prompt):
                full_response += chunk
                yield {"type": "message_delta", "delta": chunk}

            # Save assistant message & update agent run status
            await self.memory_manager.save_message(
                conversation_id=conversation_id,
                sender_type="assistant",
                sender_name="ULTRON",
                content=full_response
            )
            agent_run.status = "completed"
            agent_run.output_result = full_response
            agent_run.completed_at = datetime.utcnow()
            await self.db.commit()

            yield {"type": "message_complete", "full_content": full_response}
            return

        # Check for Memory Intent ("remember that ...")
        if "remember" in user_input.lower():
            mem_content = user_input.replace("remember", "").replace("Remember", "").strip()
            if mem_content:
                await self.memory_manager.add_long_term_memory(user_id, mem_content, importance=4)
                yield {"type": "agent_progress", "agent": "commander", "detail": f"Saved facts to long-term memory: '{mem_content}'"}

        # Normal Agent Orchestration Stream
        yield {"type": "agent_progress", "agent": "commander", "detail": "Streaming response from ULTRON Core AI..."}

        full_response = ""
        async for chunk in self.model_manager.stream(context_prompt):
            full_response += chunk
            yield {"type": "message_delta", "delta": chunk}

        # Save assistant message & complete agent run
        await self.memory_manager.save_message(
            conversation_id=conversation_id,
            sender_type="assistant",
            sender_name="ULTRON",
            content=full_response
        )

        agent_run.status = "completed"
        agent_run.output_result = full_response
        agent_run.completed_at = datetime.utcnow()
        await self.db.commit()

        yield {"type": "message_complete", "full_content": full_response}

    def _detect_tool_intent(self, text: str) -> Optional[tuple[str, Dict[str, Any]]]:
        """Detect direct tool invocations from user input text."""
        text_lower = text.lower()
        if "calculate" in text_lower or "math" in text_lower or "eval" in text_lower:
            expr = text
            for kw in ["calculate", "math", "eval", "what is"]:
                expr = re.sub(rf"\b{kw}\b", "", expr, flags=re.IGNORECASE)
            expr = expr.strip(" ?:=.").replace("x", "*")
            if expr:
                return ("calculator", {"expression": expr})

        elif "search" in text_lower or "find info" in text_lower:
            query = re.sub(r"\b(search|find info for|google|look up)\b", "", text, flags=re.IGNORECASE).strip()
            return ("web_search", {"query": query or text})

        elif "what time" in text_lower or "current date" in text_lower or "datetime" in text_lower:
            return ("get_current_datetime", {})

        return None
