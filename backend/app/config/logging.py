import logging
import sys


import json
from datetime import datetime, timezone
from app.config.settings import settings


class JSONLogFormatter(logging.Formatter):
    """Structured JSON Formatter for Production Logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "file": f"{record.filename}:{record.lineno}",
            "environment": settings.ENVIRONMENT
        }
        if hasattr(record, "request_id"):
            log_obj["request_id"] = getattr(record, "request_id")
        if hasattr(record, "workflow_id"):
            log_obj["workflow_id"] = getattr(record, "workflow_id")
        return json.dumps(log_obj)


def setup_logging():
    """Configure structured logging for ULTRON Backend."""
    handler = logging.StreamHandler(sys.stdout)
    if settings.ENVIRONMENT.lower() == "production":
        handler.setFormatter(JSONLogFormatter())
    else:
        log_format = "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
        handler.setFormatter(logging.Formatter(log_format))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [handler]

    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("aiomysql").setLevel(logging.WARNING)


logger = logging.getLogger("ULTRON")

