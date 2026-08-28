import os
import re
from urllib.parse import urlparse
from typing import Tuple, List, Optional
from app.config.settings import settings


class BrowserPolicy:
    """Enforces safety rules, scheme restrictions, domain access policy, and action step limits for browser sessions."""

    ALLOWED_SCHEMES = {"http", "https"}
    BLOCKED_SCHEMES = {"file", "javascript", "data", "ftp", "chrome", "about"}

    @classmethod
    def get_allowed_domains(cls) -> List[str]:
        raw = os.environ.get("BROWSER_ALLOWED_DOMAINS", settings.BROWSER_ALLOWED_DOMAINS)
        if not raw or raw.strip() == "*":
            return ["*"]
        return [d.strip().lower() for d in raw.split(",") if d.strip()]

    @classmethod
    def validate_url(cls, url: str) -> Tuple[bool, str]:
        """Validate URL scheme and domain according to environment policy.

        Returns (is_allowed, reason_or_cleaned_url).
        """
        if not url or not isinstance(url, str):
            return False, "Invalid URL string provided."

        url_clean = url.strip()
        parsed = urlparse(url_clean)

        scheme = parsed.scheme.lower()
        if not scheme:
            # Default to https if no scheme provided
            url_clean = f"https://{url_clean}"
            parsed = urlparse(url_clean)
            scheme = parsed.scheme.lower()

        if scheme in cls.BLOCKED_SCHEMES or scheme not in cls.ALLOWED_SCHEMES:
            return False, f"Blocked protocol scheme: '{scheme}://'. Only http and https protocols are allowed."

        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return False, "Invalid host in URL."

        allowed_domains = cls.get_allowed_domains()
        if "*" in allowed_domains:
            return True, url_clean

        # Check domain whitelist
        for domain in allowed_domains:
            if hostname == domain or hostname.endswith(f".{domain}"):
                return True, url_clean

        return False, f"Domain '{hostname}' is not in the allowed browser domains policy."

    @classmethod
    def is_action_allowed(
        self,
        action_name: str,
        step_count: int,
        nav_count: int,
        click_count: int,
        read_count: int
    ) -> Tuple[bool, str]:
        """Check action against step counter limits."""
        if step_count >= settings.MAX_BROWSER_STEPS:
            return False, f"Exceeded MAX_BROWSER_STEPS limit ({settings.MAX_BROWSER_STEPS})."

        if action_name == "browser_navigate" and nav_count >= settings.MAX_NAVIGATIONS:
            return False, f"Exceeded MAX_NAVIGATIONS limit ({settings.MAX_NAVIGATIONS})."

        if action_name == "browser_click" and click_count >= settings.MAX_CLICKS:
            return False, f"Exceeded MAX_CLICKS limit ({settings.MAX_CLICKS})."

        if action_name == "browser_read_page" and read_count >= settings.MAX_PAGE_READS:
            return False, f"Exceeded MAX_PAGE_READS limit ({settings.MAX_PAGE_READS})."

        return True, "Action allowed"
