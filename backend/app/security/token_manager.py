import logging
import time
from typing import Optional, Dict, Any, Set
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.config.settings import settings

logger = logging.getLogger("ULTRON.Security.TokenManager")


class TokenManager:
    """Production Token Manager supporting Access Token issuance, Refresh Token rotation,
    token revocation blacklist, and login attempt rate limiting.
    """

    def __init__(self):
        self._revoked_tokens: Set[str] = set()
        self._login_attempts: Dict[str, list] = {}

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a signed JWT access token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    def create_refresh_token(self, data: dict) -> str:
        """Create a signed JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token, ensuring it is not revoked."""
        if token in self._revoked_tokens:
            logger.warning("Attempted use of revoked JWT token.")
            return None
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None

    def revoke_token(self, token: str) -> None:
        """Revoke a token (add to blacklist)."""
        self._revoked_tokens.add(token)
        logger.info("JWT token successfully added to revocation blacklist.")

    def is_token_revoked(self, token: str) -> bool:
        """Check if token is in blacklist."""
        return token in self._revoked_tokens

    def check_login_rate_limit(self, identifier: str, max_attempts: int = 5, window_seconds: int = 60) -> bool:
        """Check if login attempts exceed brute-force threshold within window."""
        now = time.time()
        attempts = [t for t in self._login_attempts.get(identifier, []) if now - t < window_seconds]
        self._login_attempts[identifier] = attempts
        if len(attempts) >= max_attempts:
            logger.warning("Brute force protection triggered for identifier '%s'", identifier)
            return False
        return True

    def record_login_attempt(self, identifier: str) -> None:
        """Record a login attempt timestamp."""
        now = time.time()
        if identifier not in self._login_attempts:
            self._login_attempts[identifier] = []
        self._login_attempts[identifier].append(now)


token_manager = TokenManager()
