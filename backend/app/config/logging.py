import logging
import sys


def setup_logging():
    """Configure structured logging for ULTRON Backend."""
    log_format = (
        "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s"
    )
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("aiomysql").setLevel(logging.WARNING)


logger = logging.getLogger("ULTRON")
