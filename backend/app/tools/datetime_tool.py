from datetime import datetime


def get_current_datetime() -> str:
    """Returns current system UTC date and time."""
    now = datetime.utcnow()
    return f"Current System UTC Time: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}"
