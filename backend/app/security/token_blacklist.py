import logging
from typing import Set
from datetime import datetime

logger = logging.getLogger("ULTRON.TokenBlacklist")


class TokenBlacklist:
    """In-memory and database token revocation tracker for logout invalidation and refresh token rotation."""

    def __init__(self):
        self._revoked_tokens: Set[str] = set()

    def revoke_token(self, token: str) -> None:
        """Mark a token string as revoked."""
        if token:
            self._revoked_tokens.add(token.strip())
            logger.info("Revoked access/refresh token")

    def is_token_revoked(self, token: str) -> bool:
        """Check if a token has been revoked."""
        if not token:
            return True
        return token.strip() in self._revoked_tokens


# Global singleton instance
token_blacklist = TokenBlacklist()
