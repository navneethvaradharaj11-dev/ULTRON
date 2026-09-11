import time
from typing import Dict, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config.settings import settings

# In-memory sliding window request tracker per IP/User
_ip_request_timestamps: Dict[str, List[float]] = {}


class ServerRateLimiterMiddleware(BaseHTTPMiddleware):
    """Server-side sliding window rate limiting middleware protecting REST endpoints against abuse."""

    async def dispatch(self, request: Request, call_next):
        # Exempt health endpoints from rate limiting
        if request.url.path.startswith("/api/v1/health") or request.url.path.startswith("/metrics"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        window = 60.0  # 1 minute window
        limit = settings.RATE_LIMIT_PER_MINUTE

        timestamps = [t for t in _ip_request_timestamps.get(client_ip, []) if now - t < window]
        _ip_request_timestamps[client_ip] = timestamps

        if len(timestamps) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Too many requests in current window."}
            )

        _ip_request_timestamps[client_ip].append(now)
        return await call_next(request)
