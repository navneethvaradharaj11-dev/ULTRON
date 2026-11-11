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
        self.model_manager = model_manager or ModelManager(fallback_provider="mock")
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
        agent_run: Any = AgentRun(
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
        yield {"type": "agent_started", "agent": "commander", "run_id": str(agent_run.id), "status": "Analyzing request and context..."}

        # Build Context with history & long-term memories
        history = await self.memory_manager.get_conversation_history(conversation_id, limit=settings.MAX_CONTEXT_MESSAGES)
        memories = await self.memory_manager.get_long_term_memories(user_id)
        context_prompt = self.context_builder.build_prompt_with_context(user_input, history, memories)

        # Check for single-tool direct execution triggers (calculator, web_search, get_current_datetime)
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
            tool_call_rec: Any = ToolCallModel(
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
            if tool_name == "launch_desktop_app":
                res_obj = tool_res.get("result")
                if isinstance(res_obj, dict):
                    full_response = res_obj.get("result", f"✅ Launched {res_obj.get('app', 'Application')}.")
                else:
                    full_response = str(res_obj or "✅ Application launched successfully.")
                yield {"type": "message_delta", "delta": full_response}
            else:
                synthesis_prompt = (
                    "System: You are ULTRON, the Agentic AI Operating System running locally on this computer. "
                    "You execute real actions on the user's system via native tools. Never claim you cannot control the local computer. "
                    "Always reply in clean, direct, natural language. DO NOT output JSON, code blocks, or raw parameter dictionaries.\n"
                    f"User asked: {user_input}\nTool '{tool_name}' produced: {tool_output_str}\nSummarize the answer clearly."
                )
                full_response = ""
                async for chunk in self.model_manager.stream(synthesis_prompt):
                    full_response += chunk

                # Guard against raw JSON dumps from synthesis models
                cleaned_resp = full_response.strip()
                if cleaned_resp.startswith("{") and cleaned_resp.endswith("}"):
                    try:
                        parsed = json.loads(cleaned_resp)
                        if "query" in parsed:
                            full_response = f"🔍 Searching for **{parsed['query']}**..."
                        elif "message" in parsed:
                            full_response = str(parsed["message"])
                        elif "result" in parsed:
                            full_response = str(parsed["result"])
                    except Exception:
                        pass

                yield {"type": "message_delta", "delta": full_response}

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

        # Parse Intent & Risk via IntentEngine
        from app.core.intent_engine import IntentEngine
        from app.orchestration.orchestrator import WorkflowOrchestrator

        intent = IntentEngine.parse_intent(user_input)

        # Multi-Step or High-Risk DAG Execution Routing
        if intent.intent_type in ["RESEARCH_AND_ANALYSIS", "CODE_GENERATION_AND_TEST", "INTEGRATION_GITHUB", "INTEGRATION_CALENDAR", "INTEGRATION_EMAIL"] or intent.risk_level == "HIGH":
            yield {"type": "agent_progress", "agent": "commander", "detail": f"Multi-step workflow goal identified: '{intent.goal}'. Initiating DAG orchestrator..."}
            orchestrator: Any = WorkflowOrchestrator(self.db)
            wf: Any = await orchestrator.create_workflow(user_id=user_id, goal=intent.goal)
            step_count = len(getattr(wf, 'steps', getattr(wf, 'tasks', [])))
            yield {"type": "agent_progress", "agent": "orchestrator", "detail": f"Created workflow '{wf.workflow_id}' with {step_count} DAG steps."}

            wf_response = ""
            async for event in orchestrator.execute_workflow(wf.workflow_id, user_id):
                event_type = event.get("event_type") or event.get("type")
                if event_type == "APPROVAL_REQUIRED" or event.get("status") == "WAITING_FOR_APPROVAL":
                    yield {
                        "type": "approval_required",
                        "workflow_id": wf.workflow_id,
                        "approval_id": event.get("approval_id", f"appr-{wf.workflow_id}"),
                        "tool_name": event.get("action_type", "Workflow Action"),
                        "message": event.get("reason", "Action requires user approval.")
                    }
                    agent_run.status = "blocked"
                    await self.db.commit()
                    return
                elif event_type in ["TASK_STARTED", "TASK_COMPLETED"]:
                    yield {
                        "type": "agent_progress",
                        "agent": event.get("assigned_agent", "specialist"),
                        "detail": f"Task '{event.get('name')}': {event.get('status', 'running')}"
                    }

            # Fetch workflow result summary
            orch_repo: Any = getattr(orchestrator, "repo", getattr(orchestrator, "workflow_repo", None))
            res = await orch_repo.get_result(wf.workflow_id, user_id) if orch_repo else None
            wf_response = res.summary if res else f"Workflow '{wf.workflow_id}' completed successfully."
            
            yield {"type": "message_delta", "delta": wf_response}
            await self.memory_manager.save_message(
                conversation_id=conversation_id,
                sender_type="assistant",
                sender_name="ULTRON",
                content=wf_response
            )
            agent_run.status = "completed"
            agent_run.output_result = wf_response
            agent_run.completed_at = datetime.utcnow()
            await self.db.commit()
            yield {"type": "message_complete", "full_content": wf_response}
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
        text_lower = text.lower().strip()

        alias_map = {
            "store": "store",
            "microsoft store": "store",
            "windows store": "store",
            "whatsapp": "whatsapp",
            "spotify": "spotify",
            "music": "spotify",
            "notepad": "notepad",
            "calc": "calc",
            "calculator": "calculator",
            "settings": "settings",
            "camera": "camera",
            "photos": "photos",
            "paint": "paint",
            "terminal": "terminal",
            "cmd": "cmd",
            "powershell": "powershell",
            "chrome": "chrome",
            "edge": "edge",
            "browser": "browser",
            "code": "code",
            "vscode": "vscode",
            "explorer": "explorer",
            "files": "explorer",
            "task manager": "task manager",
            "taskmgr": "taskmgr",
            "youtube": "youtube",
            "github": "github",
            "gmail": "gmail",
            "chatgpt": "chatgpt",
            "downloads": "downloads",
            "documents": "documents",
            "pictures": "pictures",
            "recycle bin": "recycle bin",
            "control panel": "control panel",
            "discord": "discord",
            "telegram": "telegram",
            "steam": "steam",
            "desktop": "desktop",
            "c drive": "c drive",
            "d drive": "d drive",
            "e drive": "e drive",
        }

        # 0. System Controls (Volume, Media, Battery, Lock, Screenshot, Desktop, Recycle Bin, Telemetry, Specs, Clipboard, Window, Voice)
        if re.search(r"^(?:volume\s+up|increase\s+volume|turn\s+up\s+(?:the\s+)?volume|louder)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "volume_up"})
        if re.search(r"^(?:volume\s+down|decrease\s+volume|turn\s+down\s+(?:the\s+)?volume|lower\s+(?:the\s+)?volume|quieter)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "volume_down"})
        if re.search(r"^(?:mute|unmute|silence|toggle\s+mute)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "mute"})
        if re.search(r"^(?:pause\s+music|pause\s+song|pause|resume\s+music|resume\s+song|unpause|stop\s+music)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "media_play_pause"})
        if re.search(r"^(?:next\s+song|next\s+track|skip\s+song|skip\s+track|next)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "media_next"})
        if re.search(r"^(?:previous\s+song|previous\s+track|prev\s+song|prev\s+track|last\s+song)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "media_prev"})
        if re.search(r"^(?:lock\s+pc|lock\s+screen|lock\s+computer|lock\s+workstation|lock)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "lock"})
        if re.search(r"^(?:battery(?:\s+status|\s+percentage|\s+level)?|how\s+much\s+battery(?:\s+is\s+left)?|what\s+is\s+(?:the\s+)?battery)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "battery"})
        if re.search(r"^(?:system\s+info|specs|system\s+specs|hardware\s+specs|telemetry|ram\s+usage|memory\s+usage|disk\s+space|storage\s+status|pc\s+info)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "system_info"})
        if re.search(r"^(?:clipboard|read\s+clipboard|what\s+is\s+in\s+(?:my\s+)?clipboard|paste)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "clipboard"})
        if re.search(r"^(?:take\s+(?:a\s+)?screenshot|screenshot|capture\s+screen|screen\s+capture|capture\s+desktop)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "screenshot"})
        if re.search(r"^(?:minimize\s+all|show\s+desktop|minimize\s+windows)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "show_desktop"})
        if re.search(r"^(?:empty\s+recycle\s+bin|clear\s+recycle\s+bin|clean\s+recycle\s+bin)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "empty_recycle_bin"})
        if re.search(r"^(?:sleep\s+pc|sleep\s+computer|sleep)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "sleep"})

        # Window & Tab Management
        if re.search(r"^(?:maximize\s+window|maximize)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "maximize"})
        if re.search(r"^(?:minimize\s+window|minimize\s+active)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "minimize"})
        if re.search(r"^(?:snap\s+(?:window\s+)?left|snap\s+left)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "snap_left"})
        if re.search(r"^(?:snap\s+(?:window\s+)?right|snap\s+right)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "snap_right"})
        if re.search(r"^(?:switch\s+window|alt\s+tab|next\s+window)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "switch_window"})
        if re.search(r"^(?:task\s+view|virtual\s+desktops)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "task_view"})
        if re.search(r"^(?:close\s+window|close\s+this\s+window)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "close_window"})
        if re.search(r"^(?:new\s+tab|open\s+new\s+tab)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "new_tab"})
        if re.search(r"^(?:close\s+tab|close\s+this\s+tab)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "close_tab"})
        if re.search(r"^(?:reopen\s+tab|restore\s+tab)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "reopen_tab"})

        # Voice Speech Output (Native TTS)
        speak_match = re.search(r"^(?:say|speak|talk)\s+(?P<text>.+)$", text_lower)
        if speak_match:
            text_to_say = speak_match.group("text").strip()
            return ("launch_desktop_app", {"app_name": "system_control", "target": f"speak_{text_to_say}"})

        # Copy to Clipboard
        copy_match = re.search(r"^(?:copy|set\s+clipboard)\s+(?:to\s+clipboard\s+)?(?P<text>.+)$", text_lower)
        if copy_match:
            val = copy_match.group("text").strip()
            return ("launch_desktop_app", {"app_name": "system_control", "target": f"set_clipboard_{val}"})

        # File & Folder Operations
        create_folder_match = re.search(r"^(?:create\s+folder|make\s+folder|new\s+folder)\s+(?P<name>[a-zA-Z0-9_\-\s]+?)(?:\s+(?:on|in)\s+desktop)?$", text_lower)
        if create_folder_match:
            fname = create_folder_match.group("name").strip()
            return ("launch_desktop_app", {"app_name": "system_control", "target": f"create_folder_desktop_{fname}"})

        if re.search(r"^(?:list\s+(?:files\s+in\s+)?downloads|list\s+downloads\s+files|show\s+downloads(?:\s+files)?)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "list_downloads"})
        if re.search(r"^(?:list\s+(?:files\s+(?:on|in)\s+)?desktop|list\s+desktop\s+files|show\s+desktop(?:\s+files)?)$", text_lower):
            return ("launch_desktop_app", {"app_name": "system_control", "target": "list_desktop"})

        # 1. Close / Terminate Application (e.g. "close spotify", "kill chrome", "quit notepad", "close whatsapp")
        close_match = re.search(r"^(?:close|kill|terminate|quit|exit|stop)\s+(?:the\s+)?(?P<app>[a-zA-Z0-9_\-\s]+?)(?:\s+(?:on|in)\s+(?P<device>phone|mobile|android|pc|desktop))?$", text_lower)
        if close_match:
            app_to_close = close_match.group("app").strip()
            device = (close_match.group("device") or "pc").strip()
            if app_to_close not in ["music", "song", "audio"]:
                if device in ["phone", "mobile", "android"]:
                    return ("launch_desktop_app", {"app_name": "mobile", "target": f"close_{app_to_close}"})
                else:
                    return ("launch_desktop_app", {"app_name": "system_control", "target": f"close_{app_to_close}"})

        # 2. Mobile (Android) Controls
        mobile_open = re.search(r"^(?:open|launch|start|run)\s+(?:the\s+)?(?P<app>[a-zA-Z0-9_\-\s]+?)\s+(?:on|in)\s+(?:phone|mobile|android)$", text_lower)
        if not mobile_open:
            mobile_open = re.search(r"^(?:on|in)\s+(?:phone|mobile|android)\s+(?:open|launch|start|run)\s+(?:the\s+)?(?P<app>[a-zA-Z0-9_\-\s]+)$", text_lower)
        if mobile_open:
            app_name = mobile_open.group("app").strip()
            return ("launch_desktop_app", {"app_name": "mobile", "target": f"open_{app_name}"})

        if re.search(r"^(?:check|list|show)\s+(?:phone|mobile|android)(?:\s+(?:devices|status|connection))?$", text_lower):
            return ("launch_desktop_app", {"app_name": "mobile", "target": "devices"})

        connect_phone = re.search(r"^(?:connect|pair)\s+(?:to\s+)?(?:phone|mobile|android)\s*(?P<ip>[0-9.:]+)?$", text_lower)
        if connect_phone:
            ip = connect_phone.group("ip") or ""
            return ("launch_desktop_app", {"app_name": "mobile", "target": f"connect_{ip}"})

        if re.search(r"^(?:take\s+(?:a\s+)?(?:screenshot|screen\s+capture)\s+(?:on|of)\s+(?:phone|mobile|android))$", text_lower):
            return ("launch_desktop_app", {"app_name": "mobile", "target": "screenshot"})

        phone_type = re.search(r"^(?:type|write)\s+(?P<text>.+?)\s+(?:on|in)\s+(?:phone|mobile|android)$", text_lower)
        if phone_type:
            return ("launch_desktop_app", {"app_name": "mobile", "target": f"type_{phone_type.group('text').strip()}"})

        phone_call = re.search(r"^(?:call|dial)\s+(?P<num>[0-9+\s\-]+?)(?:\s+(?:on|from)\s+(?:phone|mobile|android))?$", text_lower)
        if phone_call:
            return ("launch_desktop_app", {"app_name": "mobile", "target": f"call_{phone_call.group('num').strip()}"})

        if re.search(r"^(?:phone\s+battery|battery\s+(?:of|on)\s+phone|mobile\s+battery)$", text_lower):
            return ("launch_desktop_app", {"app_name": "mobile", "target": "battery"})

        phone_key = re.search(r"^(?:press|tap)\s+(?P<key>home|back|enter|recents|power|lock)\s+(?:on|in)\s+(?:phone|mobile|android)$", text_lower)
        if phone_key:
            return ("launch_desktop_app", {"app_name": "mobile", "target": phone_key.group("key").strip()})

        # 3. Dedicated Search Engines & Portals
        wiki_match = re.search(r"^(?:search\s+wikipedia\s+(?:for\s+)?(?P<q1>.+)|wiki\s+(?P<q2>.+))$", text_lower)
        if wiki_match:
            q = (wiki_match.group("q1") or wiki_match.group("q2")).strip()
            return ("launch_desktop_app", {"app_name": "wikipedia", "target": q})

        gh_match = re.search(r"^(?:search\s+github\s+(?:for\s+)?(?P<q1>.+)|github\s+search\s+(?P<q2>.+))$", text_lower)
        if gh_match:
            q = (gh_match.group("q1") or gh_match.group("q2")).strip()
            return ("launch_desktop_app", {"app_name": "github", "target": q})

        reddit_match = re.search(r"^(?:search\s+reddit\s+(?:for\s+)?(?P<q1>.+)|reddit\s+(?P<q2>.+))$", text_lower)
        if reddit_match:
            q = (reddit_match.group("q1") or reddit_match.group("q2")).strip()
            return ("launch_desktop_app", {"app_name": "reddit", "target": q})

        amazon_match = re.search(r"^(?:search\s+amazon\s+(?:for\s+)?(?P<q1>.+)|amazon\s+(?P<q2>.+))$", text_lower)
        if amazon_match:
            q = (amazon_match.group("q1") or amazon_match.group("q2")).strip()
            return ("launch_desktop_app", {"app_name": "amazon", "target": q})

        maps_match = re.search(r"^(?:search\s+maps\s+(?:for\s+)?(?P<q1>.+)|find\s+(?P<q2>.+?)\s+on\s+maps)$", text_lower)
        if maps_match:
            q = (maps_match.group("q1") or maps_match.group("q2")).strip()
            return ("launch_desktop_app", {"app_name": "maps", "target": q})

        # 4. Google Web Search & Direct Web Browsing
        google_search = re.search(r"^(?:search\s+(?:for\s+)?(?P<q1>.+?)\s+on\s+google|google\s+(?:for\s+)?(?P<q2>.+))$", text_lower)
        if google_search:
            q = (google_search.group("q1") or google_search.group("q2")).strip()
            return ("launch_desktop_app", {"app_name": "chrome", "target": f"https://www.google.com/search?q={q}"})

        web_url = re.search(r"^(?:open|go\s+to|visit)\s+(?:website\s+)?(?P<url>https?://[^\s]+|[a-zA-Z0-9-]+\.(?:com|org|net|io|dev|app|ai)[^\s]*)$", text_lower)
        if web_url:
            url = web_url.group("url").strip()
            if not url.startswith("http"):
                url = "https://" + url
            return ("launch_desktop_app", {"app_name": "browser", "target": url})

        # 1. Media playback intent (e.g. "play coldplay on spotify", "play a song", "play music", "play believer on youtube")
        play_match = re.search(r"^(?:play|listen to)\s+(?P<track>.+?)(?:\s+(?:on|in)\s+(?P<app>spotify|youtube))?$", text_lower)
        if play_match:
            track = play_match.group("track").strip()
            app = (play_match.group("app") or "spotify").strip().lower()
            if track in ["a song", "some music", "music", "song", "songs"]:
                track = "Today's Top Hits"
            return ("launch_desktop_app", {"app_name": app, "target": track})

        # 1. Compound: "open <app> and (play|search|do) <target>" (e.g. "open spotify and play a song", "open youtube and search lofi")
        compound_match = re.search(
            r"^(?:open|launch|start|run)\s+(?:the\s+)?(?P<app>[a-zA-Z0-9_\-\s]+?)\s+and\s+(?:play|search|find|listen to|watch)?\s*(?P<target>.+)$",
            text_lower
        )
        if compound_match:
            app_raw = compound_match.group("app").strip()
            target_raw = compound_match.group("target").strip()
            canonical_app = app_raw
            for alias, canonical in alias_map.items():
                if alias in app_raw:
                    canonical_app = canonical
                    break
            if canonical_app in ["spotify", "youtube"] and target_raw in ["a song", "some music", "music", "song", "songs", "play a song"]:
                target_raw = "Today's Top Hits"
            return ("launch_desktop_app", {"app_name": canonical_app, "target": target_raw})

        # 2. In-App Searches (e.g. "in microsoft store search whatsapp", "search coldplay on spotify", "in youtube search lofi")
        in_app_search = re.search(
            r"^(?:in\s+(?:the\s+)?(?P<app1>microsoft\s+store|store|spotify|youtube|google)\s+search\s+(?:for\s+)?(?P<q1>.+)|search\s+(?:for\s+)?(?P<q2>.+?)\s+(?:in|on)\s+(?:the\s+)?(?P<app2>microsoft\s+store|store|spotify|youtube|google))$",
            text_lower
        )
        if in_app_search:
            app = (in_app_search.group('app1') or in_app_search.group('app2')).strip().lower()
            query = (in_app_search.group('q1') or in_app_search.group('q2')).strip()
            canonical_app = "store" if "store" in app else app
            return ("launch_desktop_app", {"app_name": canonical_app, "target": query})

        # 3. App Install / Download (e.g. "install whatsapp", "download spotify", "get telegram")
        install_match = re.search(r"^(?:install|download|get)\s+([a-zA-Z0-9_\-\s]+)$", text_lower)
        if install_match:
            app_to_install = install_match.group(1).strip()
            app_to_install = re.sub(r"\b(the|app|application|program)\b", "", app_to_install).strip()
            if app_to_install and not any(kw in app_to_install for kw in ["file", "doc", "code", "repo"]):
                return ("launch_desktop_app", {"app_name": "store", "target": app_to_install})

        # 4. Check for Desktop App Launching (e.g. "open whatsapp", "launch spotify", "open store", "open notepad")
        open_match = re.search(r"\b(open|launch|start|run)\s+(?:the\s+)?([a-zA-Z0-9_\-\s]+)", text_lower)
        if open_match:
            app_raw = open_match.group(2).strip()
            app_raw = re.sub(r"\b(the|desktop|app|application|program|please)\b", "", app_raw).strip()
            
            alias_map = {
                "store": "store",
                "microsoft store": "store",
                "windows store": "store",
                "whatsapp": "whatsapp",
                "spotify": "spotify",
                "notepad": "notepad",
                "calc": "calc",
                "calculator": "calculator",
                "settings": "settings",
                "camera": "camera",
                "terminal": "terminal",
                "cmd": "cmd",
                "chrome": "chrome",
                "edge": "edge",
                "browser": "browser",
                "code": "code",
                "vscode": "vscode",
                "explorer": "explorer",
                "files": "explorer",
                "task manager": "task manager",
                "taskmgr": "taskmgr",
                "youtube": "youtube",
                "github": "github",
                "gmail": "gmail",
                "chatgpt": "chatgpt",
                "downloads": "downloads",
                "documents": "documents",
                "pictures": "pictures",
                "recycle bin": "recycle bin",
                "control panel": "control panel",
                "powershell": "powershell",
                "discord": "discord",
                "telegram": "telegram",
                "steam": "steam"
            }
            
            for alias, canonical in alias_map.items():
                if alias in app_raw:
                    return ("launch_desktop_app", {"app_name": canonical})
            
            # If a clean single/double-word app name was requested, pass it directly
            if app_raw and len(app_raw.split()) <= 3 and not any(kw in app_raw for kw in ["file", "code", "model", "test", "doc"]):
                return ("launch_desktop_app", {"app_name": app_raw})

        # 4. Math / Calculation
        if "calculate" in text_lower or "math" in text_lower or "eval" in text_lower:
            expr = text
            for kw in ["calculate", "math", "eval", "what is"]:
                expr = re.sub(rf"\b{kw}\b", "", expr, flags=re.IGNORECASE)
            expr = expr.strip(" ?:=.").replace("x", "*")
            if expr:
                return ("calculator", {"expression": expr})

        # 5. Datetime
        elif "what time" in text_lower or "current date" in text_lower or "datetime" in text_lower:
            return ("get_current_datetime", {})

        # 6. Web Search
        elif "search" in text_lower or "find info" in text_lower:
            query = re.sub(r"\b(search|find info for|google|look up)\b", "", text, flags=re.IGNORECASE).strip()
            return ("web_search", {"query": query or text})

        return None

    async def execute_unified_command(
        self,
        user_id: str,
        message: str,
        workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a unified user command ('ULTRON, handle this') via WorkflowOrchestrator."""
        from app.core.intent_engine import IntentEngine
        from app.core.context_engine import PersonalContextEngine
        from app.core.capability_registry import CapabilityRegistry
        from app.core.resource_budget import ResourceBudgetTracker
        from app.security.unified_security import UnifiedSecurityGate
        from app.orchestration.orchestrator import WorkflowOrchestrator

        # 1. Intent Parsing
        intent = IntentEngine.parse_intent(message)

        # 2. Context Building
        ctx_engine = PersonalContextEngine(self.db)
        ctx = await ctx_engine.build_scoped_context(user_id, intent.goal, workspace_id)

        # 3. Capability Discovery
        cap_reg = CapabilityRegistry()
        for cap in intent.required_capabilities:
            cap_desc = cap_reg.get_capability(cap)
            if cap_desc and cap_desc.status != "AVAILABLE":
                logger.warning("Capability '%s' is not fully available", cap)

        # 4. Security & Risk Evaluation
        is_sensitive, risk_msg = UnifiedSecurityGate.evaluate_command_risk(intent.risk_level, intent.required_approval)

        # 5. Resource Budget Tracker Initialization
        budget = ResourceBudgetTracker(max_tool_calls=50, max_runtime_seconds=600)

        # 6. Workflow Creation & Dispatch
        orchestrator = WorkflowOrchestrator(self.db)
        wf = await orchestrator.create_workflow(user_id=user_id, goal=intent.goal)

        return {
            "command_status": "WORKFLOW_CREATED",
            "workflow_id": wf.workflow_id,
            "intent": intent.model_dump() if hasattr(intent, "model_dump") else intent.dict(),
            "has_context": ctx["has_context"],
            "requires_approval": is_sensitive,
            "risk_message": risk_msg
        }

