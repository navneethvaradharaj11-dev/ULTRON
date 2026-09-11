import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware for injecting and propagating request correlation IDs (`X-Correlation-ID`)."""

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or f"req-{uuid.uuid4().hex[:12]}"
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
