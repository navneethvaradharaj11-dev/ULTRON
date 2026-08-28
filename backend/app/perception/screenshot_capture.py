import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("ULTRON.ScreenshotCapture")


class ScreenshotCapture:
    """Captures viewport or full page screenshots and associates metadata with execution/session."""

    def __init__(self, viewport_width: int = 1280, viewport_height: int = 800):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height

    async def capture_viewport(
        self,
        session_id: str,
        execution_id: str,
        page_instance: Optional[Any] = None,
        full_page: bool = False
    ) -> Dict[str, Any]:
        """Capture screenshot from page instance or fallback to deterministic canvas screenshot metadata."""
        shot_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        image_bytes: Optional[bytes] = None

        if page_instance is not None and hasattr(page_instance, "screenshot"):
            try:
                image_bytes = await page_instance.screenshot(full_page=full_page)
            except Exception as e:
                logger.warning(f"Playwright page screenshot capture error: {e}")

        # Construct metadata representation
        metadata = {
            "screenshot_id": shot_id,
            "session_id": session_id,
            "execution_id": execution_id,
            "width": self.viewport_width,
            "height": self.viewport_height,
            "full_page": full_page,
            "timestamp": timestamp,
            "has_bytes": image_bytes is not None,
            "byte_size": len(image_bytes) if image_bytes else 0,
            "format": "png"
        }

        logger.info(f"Captured screenshot '{shot_id}' for session '{session_id}' (full_page={full_page})")
        return {
            "id": shot_id,
            "metadata": metadata,
            "bytes": image_bytes,
            "width": self.viewport_width,
            "height": self.viewport_height,
            "timestamp": timestamp
        }
