import httpx
import logging
from typing import Dict, Any, Tuple, Optional
from app.browser.browser_policy import BrowserPolicy
from app.browser.page_reader import PageReader
from app.config.settings import settings

logger = logging.getLogger("ULTRON.Navigation")


class NavigationManager:
    """Handles controlled web navigation using Playwright Chromium page runtime."""

    @classmethod
    async def fetch_page(
        cls,
        url: str,
        playwright_page: Optional[Any] = None
    ) -> Tuple[bool, Dict[str, Any], str]:
        """Navigate to target URL via Playwright Chromium page instance or httpx fallback.

        Returns (success, structured_page, raw_html_or_error_msg).
        """
        is_allowed, cleaned_url_or_err = BrowserPolicy.validate_url(url)
        if not is_allowed:
            return False, {
                "url": url,
                "title": "Navigation Blocked",
                "elements": [],
                "text": cleaned_url_or_err,
                "links": []
            }, cleaned_url_or_err

        target_url = cleaned_url_or_err

        # 1. Playwright Chromium Page Navigation
        if playwright_page:
            try:
                resp = await playwright_page.goto(target_url, timeout=int(settings.BROWSER_ACTION_TIMEOUT * 1000), wait_until="domcontentloaded")
                await playwright_page.wait_for_timeout(300)  # Wait brief tick for dynamic JS execution

                final_url = playwright_page.url
                html_content = await playwright_page.content()

                structured_page = await PageReader.parse_playwright_page(playwright_page)
                return True, structured_page, html_content

            except Exception as e:
                msg = f"Playwright navigation error for '{target_url}': {str(e)}"
                logger.warning(msg)
                return False, {"url": target_url, "title": "Navigation Error", "elements": [], "text": msg, "links": []}, msg

        # 2. HTTP Fallback Navigation
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=settings.BROWSER_ACTION_TIMEOUT) as client:
                headers = {"User-Agent": "ULTRON-BrowserAgent/3.0"}
                resp = await client.get(target_url, headers=headers)
                resp.raise_for_status()

                html_content = resp.text
                final_url = str(resp.url)

                structured_page = PageReader.parse_html(final_url, html_content)
                return True, structured_page, html_content

        except httpx.TimeoutException:
            msg = f"Navigation to '{target_url}' timed out after {settings.BROWSER_ACTION_TIMEOUT}s."
            logger.warning(msg)
            return False, {"url": target_url, "title": "Timeout", "elements": [], "text": msg, "links": []}, msg

        except httpx.HTTPStatusError as e:
            msg = f"HTTP Error {e.response.status_code} while requesting '{target_url}'."
            logger.warning(msg)
            return False, {"url": target_url, "title": "HTTP Error", "elements": [], "text": msg, "links": []}, msg

        except Exception as e:
            msg = f"Failed to navigate to '{target_url}': {str(e)}"
            logger.error(msg)
            return False, {"url": target_url, "title": "Navigation Error", "elements": [], "text": msg, "links": []}, msg
