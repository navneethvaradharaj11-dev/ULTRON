import logging
from typing import Dict, Any, Optional
from app.browser.browser_manager import browser_manager
from app.browser.element_finder import ElementFinder
from app.browser.extraction import StructuredExtractor

logger = logging.getLogger("ULTRON.BrowserTools")


async def browser_navigate(url: str, session_id: Optional[str] = None, user_id: str = "default_user", execution_id: Optional[str] = None) -> Dict[str, Any]:
    """Navigate to target URL in a real Playwright Chromium browser session."""
    session = None
    if session_id:
        session, err = browser_manager.get_session(session_id, user_id)
        if err:
            return {"error": err, "success": False}
    else:
        session = await browser_manager.create_browser_session_async(user_id=user_id, execution_id=execution_id)

    success, page_data = await session.navigate(url)
    return {
        "success": success,
        "session_id": session.session_id,
        "current_url": session.current_url,
        "page": page_data
    }


async def browser_back(session_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Navigate back in real browser history."""
    session, err = browser_manager.get_session(session_id, user_id)
    if err:
        return {"error": err, "success": False}
    success, page_data = await session.back()
    return {"success": success, "session_id": session_id, "page": page_data}


async def browser_forward(session_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Navigate forward in real browser history."""
    session, err = browser_manager.get_session(session_id, user_id)
    if err:
        return {"error": err, "success": False}
    success, page_data = await session.forward()
    return {"success": success, "session_id": session_id, "page": page_data}


async def browser_reload(session_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Reload active page in real browser."""
    session, err = browser_manager.get_session(session_id, user_id)
    if err:
        return {"error": err, "success": False}
    success, page_data = await session.reload()
    return {"success": success, "session_id": session_id, "page": page_data}


async def browser_read_page(session_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Inspect live Playwright Chromium page structure and content with prompt-injection isolation."""
    session, err = browser_manager.get_session(session_id, user_id)
    if err:
        return {"error": err, "success": False}
    safe_page = await session.read_page_async()
    if "error" in safe_page:
        return {"success": False, "error": safe_page["error"]}
    return {"success": True, "session_id": session_id, "page": safe_page}


async def browser_find_element(session_id: str, query: str, element_type: Optional[str] = None, user_id: str = "default_user") -> Dict[str, Any]:
    """Identify element on live page using semantic role, visible text, or attribute matching."""
    session, err = browser_manager.get_session(session_id, user_id)
    if err:
        return {"error": err, "success": False}
    elements = session.current_page.get("elements", [])
    found = ElementFinder.find_element(elements, query, element_type=element_type)
    if not found:
        return {"success": False, "error": f"Element matching '{query}' not found."}
    return {"success": True, "session_id": session_id, "element": found}


async def browser_click(session_id: str, element_query: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Click element in live Playwright Chromium browser."""
    session, err = browser_manager.get_session(session_id, user_id)
    if err:
        return {"error": err, "success": False}
    success, result, req_appr = await session.perform_action_async("browser_click", {"element_query": element_query})
    return {
        "success": success,
        "session_id": session_id,
        "requires_approval": req_appr,
        "result": result
    }


async def browser_type(session_id: str, element_query: str, text: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Enter text into input field in live Chromium page."""
    session, err = browser_manager.get_session(session_id, user_id)
    if err:
        return {"error": err, "success": False}
    success, result, req_appr = await session.perform_action_async("browser_type", {"element_query": element_query, "text": text})
    return {
        "success": success,
        "session_id": session_id,
        "requires_approval": req_appr,
        "result": result
    }


async def browser_select(session_id: str, element_query: str, value: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Select option in dropdown element in live Chromium page."""
    session, err = browser_manager.get_session(session_id, user_id)
    if err:
        return {"error": err, "success": False}
    success, result, req_appr = await session.perform_action_async("browser_select", {"element_query": element_query, "value": value})
    return {
        "success": success,
        "session_id": session_id,
        "requires_approval": req_appr,
        "result": result
    }


async def browser_extract(session_id: str, facts: list, user_id: str = "default_user") -> Dict[str, Any]:
    """Extract structured facts from current page with citation evidence."""
    session, err = browser_manager.get_session(session_id, user_id)
    if err:
        return {"error": err, "success": False}

    source_url = session.current_url or "unknown"
    extraction_struct = StructuredExtractor.create_structured_fact_extraction(source_url, facts)

    return {
        "success": True,
        "session_id": session_id,
        "extraction": extraction_struct
    }


async def browser_screenshot(session_id: str, user_id: str = "default_user") -> Dict[str, Any]:
    """Capture real Playwright Chromium browser viewport screenshot."""
    session, err = browser_manager.get_session(session_id, user_id)
    if err:
        return {"error": err, "success": False}
    success, result, req_appr = await session.perform_action_async("browser_screenshot", {})
    return {
        "success": success,
        "session_id": session_id,
        "result": result
    }
