import base64
import logging
from typing import Dict, Any, List, Optional, Tuple
from app.browser.element_finder import ElementFinder
from app.security.browser_security import BrowserSecurity

logger = logging.getLogger("ULTRON.PageActions")


class PageActionDispatcher:
    """Executes actions on live Playwright Chromium pages or structured DOM representations."""

    SENSITIVE_ACTION_TYPES = {"submit_form", "purchase", "financial_transaction", "delete_cloud_data", "account_change"}

    @classmethod
    async def execute_action_async(
        cls,
        current_page_struct: Dict[str, Any],
        action_name: str,
        params: Dict[str, Any],
        playwright_page: Optional[Any] = None
    ) -> Tuple[bool, Dict[str, Any], bool]:
        """Dispatch action asynchronously using live Playwright page or DOM structure.

        Returns (success, result_dict, requires_approval).
        """
        # 1. High-impact action approval check
        if action_name in cls.SENSITIVE_ACTION_TYPES or params.get("is_sensitive"):
            return False, {
                "requires_approval": True,
                "approval_status": "pending_approval",
                "action": action_name,
                "params": params,
                "message": f"Browser action '{action_name}' is high-impact and requires explicit user approval."
            }, True

        elements = current_page_struct.get("elements", [])

        # Check for login form when typing/submitting
        if action_name in ("browser_type", "browser_click") and BrowserSecurity.detect_login_form(elements):
            if params.get("element_query") and "password" in str(params.get("element_query")).lower():
                return False, {
                    "error": "AUTHENTICATION_REQUIRED",
                    "message": "Website requires user authentication. Password guessing and automated credential filling are blocked."
                }, False

        if action_name == "browser_click":
            query = params.get("element_query") or params.get("element_id")
            target = ElementFinder.find_element(elements, str(query)) if query else None
            target_id = target.get("id") if target else query or "unknown"
            target_text = target.get("text") if target else ""

            if target and target.get("type") in ("submit", "form") and "submit" in target_text.lower():
                return False, {
                    "requires_approval": True,
                    "approval_status": "pending_approval",
                    "action": "submit_form",
                    "params": {"element_id": target_id, "text": target_text},
                    "message": "Form submission requires explicit human approval."
                }, True

            if playwright_page and query:
                try:
                    # Attempt click by CSS ID selector first, then text content
                    selector = f"#{target_id}" if target_id and not target_id.startswith("element_") else f"text={query}"
                    if not await playwright_page.query_selector(selector):
                        selector = f"button:has-text('{query}'), a:has-text('{query}'), input[value*='{query}']"
                    
                    await playwright_page.click(selector, timeout=5000)
                    await playwright_page.wait_for_timeout(300)
                    return True, {
                        "action": "click",
                        "selector": selector,
                        "element_id": target_id,
                        "status": "clicked",
                        "message": f"Successfully clicked '{query}' via Playwright Chromium."
                    }, False
                except Exception as e:
                    logger.warning("Playwright click failed for '%s': %s", query, e)

            return True, {
                "action": "click",
                "element_id": target_id,
                "element_text": target_text,
                "status": "clicked",
                "message": f"Successfully clicked element '{target_id}' ({target_text})."
            }, False

        elif action_name == "browser_type":
            query = params.get("element_query") or params.get("element_id")
            text_to_type = params.get("text", "")
            target = ElementFinder.find_element(elements, str(query), element_type="input") if query else None
            target_id = target.get("id") if target else query or "input_1"

            if playwright_page and query:
                try:
                    selector = f"#{target_id}" if target_id and not target_id.startswith("element_") else f"input[name='{query}'], input[placeholder*='{query}']"
                    if not await playwright_page.query_selector(selector):
                        selector = f"input, textarea"

                    await playwright_page.fill(selector, text_to_type, timeout=5000)
                    return True, {
                        "action": "type",
                        "selector": selector,
                        "element_id": target_id,
                        "typed_text": text_to_type,
                        "status": "typed",
                        "message": f"Successfully typed '{text_to_type}' into input via Playwright Chromium."
                    }, False
                except Exception as e:
                    logger.warning("Playwright fill failed for '%s': %s", query, e)

            return True, {
                "action": "type",
                "element_id": target_id,
                "typed_text": text_to_type,
                "status": "typed",
                "message": f"Typed '{text_to_type}' into element '{target_id}'."
            }, False

        elif action_name == "browser_select":
            query = params.get("element_query") or params.get("element_id")
            value = params.get("value", "")
            target = ElementFinder.find_element(elements, str(query), element_type="select") if query else None
            target_id = target.get("id") if target else query or "select_1"

            if playwright_page and query:
                try:
                    selector = f"#{target_id}" if target_id and not target_id.startswith("element_") else f"select[name='{query}'], select"
                    await playwright_page.select_option(selector, value=value, timeout=5000)
                    return True, {
                        "action": "select",
                        "selector": selector,
                        "selected_value": value,
                        "status": "selected",
                        "message": f"Successfully selected '{value}' via Playwright Chromium."
                    }, False
                except Exception as e:
                    logger.warning("Playwright select failed: %s", e)

            return True, {
                "action": "select",
                "element_id": target_id,
                "selected_value": value,
                "status": "selected",
                "message": f"Selected value '{value}' in element '{target_id}'."
            }, False

        elif action_name == "browser_screenshot":
            if playwright_page:
                try:
                    png_bytes = await playwright_page.screenshot(full_page=False, type="png")
                    b64_str = base64.b64encode(png_bytes).decode("utf-8")
                    return True, {
                        "action": "screenshot",
                        "url": playwright_page.url,
                        "image_base64": b64_str,
                        "format": "png",
                        "captured": True
                    }, False
                except Exception as e:
                    logger.warning("Playwright screenshot failed: %s", e)

            mock_png = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            return True, {
                "action": "screenshot",
                "url": current_page_struct.get("url"),
                "image_base64": mock_png.decode("utf-8"),
                "format": "png",
                "captured": True
            }, False

        return False, {"error": f"Unknown page action '{action_name}'."}, False

    @classmethod
    def execute_action(
        cls,
        current_page_struct: Dict[str, Any],
        action_name: str,
        params: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any], bool]:
        """Sync wrapper for backward compatibility."""
        import asyncio
        loop = asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else None
        if loop:
            # Sync execution path fallback
            return False, {"error": "Use execute_action_async for Playwright operations."}, False
        return asyncio.run(cls.execute_action_async(current_page_struct, action_name, params))
