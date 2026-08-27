# ULTRON System Architecture Overview

PROJECT ULTRON is built as a modular Agentic AI Operating System.

## Stack Overview
- **Frontend**: Dart / Flutter
- **Backend / Core Engine**: Python 3.14 / FastAPI
- **Web Layer**: JavaScript / HTML5 / CSS3
- **Primary Database**: MySQL
- **Communication Protocol**: REST API + WebSocket (Structured real-time event streaming)

## Core Components
1. **UltronCore**: Main orchestrator managing prompt building, context windows, long-term memory retrieval, agent step dispatch, and tool execution lifecycle.
2. **ModelManager**: Provider-agnostic AI model interface supporting Google Gemini, OpenAI, Anthropic, and deterministic Mock providers.
3. **AgentEngine**: Multi-agent team consisting of Commander, Planner, Researcher, Coder, and Reviewer.
4. **ToolRegistry**: Safe sandbox environment with path sandboxing, parameter schemas, execution timeouts (`TOOL_TIMEOUT`), security policies, and audit logging.
5. **MemoryEngine**: Relational MySQL memory system maintaining short-term context, conversation message history, and long-term user preferences/facts.
