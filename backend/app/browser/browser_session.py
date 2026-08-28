import uuid
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page

from app.browser.browser_policy import BrowserPolicy
from app.browser.navigation import NavigationManager
from app.browser.page_actions import PageActionDispatcher
from app.browser.page_reader import PageReader
from app.security.browser_security import BrowserSecurity

logger = logging.getLogger("ULTRON.BrowserSession")


class BrowserSession:
    """Represents an active Playwright Chromium browser session bound to user_id, execution_id, and session_id."""

    def __init__(
        self,
        user_id: str,
        execution_id: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        self.session_id: str = session_id or f"bsession_{uuid.uuid4().hex[:8]}"
        self.user_id: str = user_id
        self.execution_id: Optional[str] = execution_id
        self.status: str = "ACTIVE"  # ACTIVE, CLOSED, ERROR
        self.current_url: Optional[str] = None
        self.current_page: Dict[str, Any] = {}
        self.history: List[str] = []
        self.history_index: int = -1
        self.created_at: datetime = datetime.utcnow()
        self.closed_at: Optional[datetime] = None

        # Playwright Chromium Runtime references (scoped to active loop)
        self._playwright_instance: Optional[Playwright] = None
        self._browser_instance: Optional[Browser] = None
        self.playwright_context: Optional[BrowserContext] = None
        self.playwright_page: Optional[Page] = None

        # Action & Loop Counters
        self.step_count: int = 0
        self.nav_count: int = 0
        self.click_count: int = 0
        self.read_count: int = 0
        self.actions_log: List[Dict[str, Any]] = []

    def check_ownership(self, requesting_user_id: str) -> bool:
        """Enforce strict multi-tenant session ownership."""
        return self.user_id == requesting_user_id

    async def _ensure_playwright_page(self) -> Optional[Page]:
        """Lazy instantiate Playwright Chromium page on the active event loop."""
        if self.status != "ACTIVE":
            return None
        if not self.playwright_page:
            try:
                self._playwright_instance = await async_playwright().start()
                self._browser_instance = await self._playwright_instance.chromium.launch(headless=True)
                self.playwright_context = await self._browser_instance.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ULTRON-Chromium/3.1",
                    viewport={"width": 1280, "height": 720}
                )
                self.playwright_page = await self.playwright_context.new_page()
            except Exception as e:
                logger.warning("Playwright launch info for session '%s': %s", self.session_id, e)
        return self.playwright_page

    async def navigate(self, url: str) -> Tuple[bool, Dict[str, Any]]:
        """Navigate to target URL using real Chromium browser instance."""
        if self.status != "ACTIVE":
            return False, {"error": "Browser session is closed."}

        is_allowed, reason = BrowserPolicy.is_action_allowed(
            "browser_navigate", self.step_count, self.nav_count, self.click_count, self.read_count
        )
        if not is_allowed:
            return False, {"error": reason}

        self.step_count += 1
        self.nav_count += 1

        pw_page = await self._ensure_playwright_page()
        success, page_struct, raw_html_or_err = await NavigationManager.fetch_page(url, playwright_page=pw_page)

        if success:
            self.current_url = page_struct.get("url", url)
            self.current_page = page_struct

            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            self.history.append(self.current_url)
            self.history_index = len(self.history) - 1

            self._log_action_internal("browser_navigate", {"url": url}, {"status": "success", "page": self.current_page})
            return True, self.current_page
        else:
            self._log_action_internal("browser_navigate", {"url": url}, {"error": raw_html_or_err}, status="FAILED")
            return False, {"error": raw_html_or_err}

    async def back(self) -> Tuple[bool, Dict[str, Any]]:
        """Navigate back in real browser history."""
        pw_page = await self._ensure_playwright_page()
        if pw_page:
            try:
                await pw_page.go_back(timeout=5000)
                self.current_page = await PageReader.parse_playwright_page(pw_page)
                self.current_url = pw_page.url
                return True, self.current_page
            except Exception as e:
                logger.warning("Playwright go_back failed: %s", e)

        if self.history_index > 0:
            self.history_index -= 1
            prev_url = self.history[self.history_index]
            return await self.navigate(prev_url)
        return False, {"error": "No previous page in navigation history."}

    async def forward(self) -> Tuple[bool, Dict[str, Any]]:
        """Navigate forward in real browser history."""
        pw_page = await self._ensure_playwright_page()
        if pw_page:
            try:
                await pw_page.go_forward(timeout=5000)
                self.current_page = await PageReader.parse_playwright_page(pw_page)
                self.current_url = pw_page.url
                return True, self.current_page
            except Exception as e:
                logger.warning("Playwright go_forward failed: %s", e)

        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            next_url = self.history[self.history_index]
            return await self.navigate(next_url)
        return False, {"error": "No forward page in navigation history."}

    async def reload(self) -> Tuple[bool, Dict[str, Any]]:
        """Reload current page in real browser."""
        pw_page = await self._ensure_playwright_page()
        if pw_page:
            try:
                await pw_page.reload(timeout=5000)
                self.current_page = await PageReader.parse_playwright_page(pw_page)
                self.current_url = pw_page.url
                return True, self.current_page
            except Exception as e:
                logger.warning("Playwright reload failed: %s", e)

        if self.current_url:
            return await self.navigate(self.current_url)
        return False, {"error": "No page loaded to reload."}

    async def read_page_async(self) -> Dict[str, Any]:
        """Inspect structured representation of live Chromium DOM page with prompt injection defense."""
        if self.status != "ACTIVE":
            return {"error": "Browser session is closed."}

        is_allowed, reason = BrowserPolicy.is_action_allowed(
            "browser_read_page", self.step_count, self.nav_count, self.click_count, self.read_count
        )
        if not is_allowed:
            return {"error": reason}

        self.step_count += 1
        self.read_count += 1

        pw_page = await self._ensure_playwright_page()
        if pw_page:
            self.current_page = await PageReader.parse_playwright_page(pw_page)

        raw_text = self.current_page.get("text", "")
        safe_text = BrowserSecurity.sanitize_untrusted_page_content(raw_text, self.current_url or "")

        safe_page = dict(self.current_page)
        safe_page["safe_text"] = safe_text

        self._log_action_internal("browser_read_page", {}, {"title": safe_page.get("title")})
        return safe_page

    def read_page(self) -> Dict[str, Any]:
        """Sync read_page wrapper."""
        raw_text = self.current_page.get("text", "")
        safe_text = BrowserSecurity.sanitize_untrusted_page_content(raw_text, self.current_url or "")
        safe_page = dict(self.current_page)
        safe_page["safe_text"] = safe_text
        return safe_page

    async def perform_action_async(self, action_name: str, params: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], bool]:
        """Perform action against live Playwright Chromium page."""
        if self.status != "ACTIVE":
            return False, {"error": "Browser session is closed."}, False

        is_allowed, reason = BrowserPolicy.is_action_allowed(
            action_name, self.step_count, self.nav_count, self.click_count, self.read_count
        )
        if not is_allowed:
            return False, {"error": reason}, False

        self.step_count += 1
        if action_name == "browser_click":
            self.click_count += 1

        pw_page = await self._ensure_playwright_page()
        success, result, req_appr = await PageActionDispatcher.execute_action_async(
            self.current_page, action_name, params, playwright_page=pw_page
        )
        status_str = "REQUIRES_APPROVAL" if req_appr else ("SUCCESS" if success else "FAILED")
        self._log_action_internal(action_name, params, result, status=status_str)

        if pw_page and success and not req_appr:
            try:
                self.current_page = await PageReader.parse_playwright_page(pw_page)
                self.current_url = pw_page.url
            except Exception:
                pass

        return success, result, req_appr

    def perform_action(self, action_name: str, params: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], bool]:
        """Sync wrapper for perform_action."""
        return asyncio.get_event_loop().run_until_complete(self.perform_action_async(action_name, params))

    async def close_async(self):
        """Asynchronously close Playwright page, context, browser, and instance."""
        self.status = "CLOSED"
        self.closed_at = datetime.utcnow()

        if self.playwright_page:
            try:
                await self.playwright_page.close()
            except Exception:
                pass
            self.playwright_page = None

        if self.playwright_context:
            try:
                await self.playwright_context.close()
            except Exception:
                pass
            self.playwright_context = None

        if self._browser_instance:
            try:
                await self._browser_instance.close()
            except Exception:
                pass
            self._browser_instance = None

        if self._playwright_instance:
            try:
                await self._playwright_instance.stop()
            except Exception:
                pass
            self._playwright_instance = None

    def close(self):
        """Sync wrapper for close."""
        self.status = "CLOSED"
        self.closed_at = datetime.utcnow()
        if self._playwright_instance or self.playwright_page:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.close_async())
                else:
                    loop.run_until_complete(self.close_async())
            except Exception:
                pass

    def _log_action_internal(
        self,
        action_type: str,
        params: Dict[str, Any],
        result: Dict[str, Any],
        status: str = "SUCCESS"
    ):
        self.actions_log.append({
            "action_id": f"act_{uuid.uuid4().hex[:8]}",
            "action_type": action_type,
            "params": params,
            "result": result,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })
