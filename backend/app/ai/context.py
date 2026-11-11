from typing import List, Dict, Any, Optional


class ContextBuilder:
    """Manages chat context window, message truncation, and long-term memory retrieval."""

    def __init__(self, max_history_messages: int = 20):
        self.max_history_messages = max_history_messages

    def build_prompt_with_context(
        self,
        user_input: str,
        messages_history: List[Dict[str, Any]],
        memories: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Combine user input, relevant history, and retrieved long-term memories into prompt."""
        prompt_parts = [
            "=== SYSTEM IDENTITY ===",
            "You are ULTRON, the Agentic AI Operating System running locally on this computer.",
            "You have direct control of the user's local operating system, desktop applications, filesystem, and tools.",
            "Never claim you are a restricted or server-only AI model that cannot interact with the local machine.",
            "Always act as an empowering, proactive personal AI assistant.",
            "CRITICAL RULES:",
            "1. NEVER simulate terminal sessions or print fake shell prompts (e.g. do NOT output 'PS C:\\Users>' or 'cmd>').",
            "2. NEVER dump raw JSON structures or function-calling argument dictionaries to the user.",
            "3. If the user asks you to open or run something, acknowledge that you are executing it or guide them directly.",
            "4. Respond naturally, concisely, and helpfully in markdown.",
            "=======================\n"
        ]

        # 1. Inject Long-Term Memories if present
        if memories and len(memories) > 0:
            prompt_parts.append("=== USER LONG-TERM MEMORIES & PREFERENCES ===")
            for mem in memories:
                prompt_parts.append(f"- [{mem.get('memory_type', 'fact')}] {mem.get('content')}")
            prompt_parts.append("=============================================\n")

        # 2. Inject Truncated Message History
        recent_messages = messages_history[-self.max_history_messages:] if len(messages_history) > self.max_history_messages else messages_history
        if recent_messages:
            prompt_parts.append("=== RECENT CONVERSATION HISTORY ===")
            for msg in recent_messages:
                sender = msg.get("sender_name", msg.get("sender_type", "User"))
                prompt_parts.append(f"{sender}: {msg.get('content')}")
            prompt_parts.append("===================================\n")

        # 3. Current User Request
        prompt_parts.append(f"User: {user_input}")

        return "\n".join(prompt_parts)
