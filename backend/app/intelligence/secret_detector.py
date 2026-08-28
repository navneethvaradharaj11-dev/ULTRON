import re
from typing import Tuple, List

SECRET_PATTERNS = [
    (re.compile(r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{16,})["\']?'), "API Key / Auth Token"),
    (re.compile(r'eyJ[a-zA-Z0-9_-]{8,}\.[a-zA-Z0-9_-]{8,}\.[a-zA-Z0-9_-]{4,}'), "JWT Token"),
    (re.compile(r'-----BEGIN\s+(RSA|EC|DSA|OPENSSH|PRIVATE)?\s*KEY-----[\s\S]+?-----END\s+(RSA|EC|DSA|OPENSSH|PRIVATE)?\s*KEY-----'), "Private Key"),

    (re.compile(r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^\s"\'\`]{6,})["\']?'), "Password Credential"),
    (re.compile(r'mysql(?:\+pymysql|\+aiomysql)?://[a-zA-Z0-9_]+:[^@]+@[a-zA-Z0-9_.:]+/'), "Database Connection String"),
    (re.compile(r'postgres(?:ql)?://[a-zA-Z0-9_]+:[^@]+@[a-zA-Z0-9_.:]+/'), "Database Connection String"),
    (re.compile(r'(?i)session[_-]?id\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{24,})["\']?'), "Session Cookie / Token"),
]


class SecretDetector:
    """Utility to scan strings and structured content for sensitive credentials before persistence."""

    @staticmethod
    def contains_secret(text: str) -> Tuple[bool, List[str]]:
        """Return True and list of detected secret types if text contains sensitive secrets."""
        if not text:
            return False, []
        
        detected = []
        for pattern, secret_type in SECRET_PATTERNS:
            if pattern.search(text):
                detected.append(secret_type)
        return len(detected) > 0, detected

    @staticmethod
    def sanitize(text: str) -> str:
        """Mask detected secrets in text string."""
        if not text:
            return text

        sanitized = text
        for pattern, secret_type in SECRET_PATTERNS:
            sanitized = pattern.sub(f"[REDACTED_{secret_type.upper().replace(' ', '_')}]", sanitized)
        return sanitized

    sanitize_text = sanitize
    detect_secrets = contains_secret


