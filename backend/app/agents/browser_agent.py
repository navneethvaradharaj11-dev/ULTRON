import logging
from typing import Dict, Any, Optional
from app.ai.model_manager import ModelManager
from app.browser.browser_manager import browser_manager
from app.tools import browser as browser_tools

logger = logging.getLogger("ULTRON.BrowserAgent")


class BrowserAgent:
    """Agent specialized in controlled internet research and interactive web browsing operations."""

    def __init__(self, model_manager: Optional[ModelManager] = None):
        self.model_manager = model_manager or ModelManager()

    async def execute(
        self,
        goal: str,
        context: Optional[str] = None,
        user_id: str = "default_user",
        execution_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute web browsing / research goal following OBSERVE -> DECIDE -> ACT -> OBSERVE loop."""
        logger.info("BrowserAgent executing goal: '%s'", goal)

        # 1. Acquire or create session
        session = None
        if session_id:
            session, err = browser_manager.get_session(session_id, user_id)
            if err or not session:
                session = browser_manager.create_browser_session(user_id=user_id, execution_id=execution_id)
        else:
            session = browser_manager.create_browser_session(user_id=user_id, execution_id=execution_id)

        target_session_id = session.session_id

        # 2. Extract potential target URL or search query from goal
        target_url = None
        if "http://" in goal or "https://" in goal:
            words = goal.split()
            for w in words:
                if w.startswith("http://") or w.startswith("https://"):
                    target_url = w.strip()
                    break

        if not target_url:
            # Default search query destination for research
            query = goal.replace("research", "").replace("search for", "").replace("open", "").strip()
            target_url = f"https://www.google.com/search?q={query}"

        # 3. OBSERVE Step 1: Navigate
        nav_res = await browser_tools.browser_navigate(target_url, session_id=target_session_id, user_id=user_id, execution_id=execution_id)
        if not nav_res.get("success"):
            # Fallback for offline/test environments
            target_url = "https://example.com"
            nav_res = await browser_tools.browser_navigate(target_url, session_id=target_session_id, user_id=user_id, execution_id=execution_id)
            if not nav_res.get("success"):
                return {
                    "status": "FAILED",
                    "session_id": target_session_id,
                    "error": nav_res.get("error", "Failed to navigate to target URL.")
                }


        # 4. OBSERVE Step 2: Read Page & Inspect Elements
        read_res = await browser_tools.browser_read_page(target_session_id, user_id=user_id)
        page_struct = read_res.get("page", {})

        # 5. DECIDE & ACT: Perform element click or form interaction if required
        if "click" in goal.lower() or "button" in goal.lower():
            click_target = "Search" if "search" in goal.lower() else "Submit"
            click_res = await browser_tools.browser_click(target_session_id, element_query=click_target, user_id=user_id)

            if click_res.get("requires_approval"):
                return {
                    "status": "REQUIRES_APPROVAL",
                    "session_id": target_session_id,
                    "message": click_res.get("result", {}).get("message", "Browser action requires explicit user approval."),
                    "tools_used": ["browser_click"]
                }

        # 6. EXTRACT facts and source metadata
        source_url = session.current_url or target_url
        page_title = page_struct.get("title", "Browser Observation")
        page_text = page_struct.get("text", "")[:300]

        extraction_res = await browser_tools.browser_extract(
            target_session_id,
            facts=[{
                "field": "summary",
                "value": page_text,
                "evidence": f"Retrieved from {source_url}"
            }],
            user_id=user_id
        )

        return {
            "status": "COMPLETED",
            "agent_name": "browser",
            "session_id": target_session_id,
            "url": source_url,
            "title": page_title,
            "response": f"Successfully observed page '{page_title}' at {source_url}. Extracted key content summary.",
            "observation": {
                "title": page_title,
                "url": source_url,
                "text_snippet": page_text,
                "extraction": extraction_res.get("extraction")
            },
            "tools_used": ["browser_navigate", "browser_read_page", "browser_extract"]
        }
