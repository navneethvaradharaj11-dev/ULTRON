import os
import hashlib
import logging
from typing import Dict, Any, List, Optional
from app.browser.browser_agentic import AgenticBrowser

logger = logging.getLogger("ULTRON.MonitorEngine")


class WebsiteMonitor:
    """Website Change Monitor utilizing Playwright with semantic change detection."""

    @staticmethod
    async def check_website_change(user_id: str, url: str, last_hash: str) -> Dict[str, Any]:
        """Fetch URL content via Playwright, extract clean text, and detect meaningful changes."""
        browser = AgenticBrowser()
        try:
            res = await browser.execute_action(user_id=user_id, action="goto", url=url)
            page_data = await browser.execute_action(user_id=user_id, action="read_page")
            clean_text = page_data.get("title", "") + "\n" + page_data.get("text_content", "")
            current_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()

            changed = (last_hash != "" and current_hash != last_hash)
            return {
                "url": url,
                "changed": changed,
                "current_hash": current_hash,
                "title": page_data.get("title", ""),
                "summary": clean_text[:200]
            }
        except Exception as e:
            logger.warning("WebsiteMonitor error checking '%s': %s", url, e)
            return {"url": url, "changed": False, "error": str(e), "current_hash": last_hash}
        finally:
            await browser.close_session(user_id)


class FileMonitor:
    """Monitors workspace directories for file additions or modifications."""

    @staticmethod
    def check_file_change(filepath: str, last_hash: str) -> Dict[str, Any]:
        if not os.path.exists(filepath):
            return {"filepath": filepath, "changed": False, "missing": True, "current_hash": last_hash}

        with open(filepath, "rb") as f:
            content = f.read()
        cur_hash = hashlib.sha256(content).hexdigest()
        changed = (last_hash != "" and cur_hash != last_hash)
        return {"filepath": filepath, "changed": changed, "current_hash": cur_hash}
