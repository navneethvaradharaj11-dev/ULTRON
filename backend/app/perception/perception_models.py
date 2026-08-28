from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BoundingBox(BaseModel):
    x: int = Field(..., description="Top-left X coordinate")
    y: int = Field(..., description="Top-left Y coordinate")
    width: int = Field(..., description="Width of bounding box in pixels")
    height: int = Field(..., description="Height of bounding box in pixels")


class VisualElement(BaseModel):
    id: str = Field(..., description="Unique element identifier")
    type: str = Field(..., description="UI component type (button, input, link, checkbox, etc.)")
    label: str = Field(default="", description="Visible text label or accessibility description")
    bbox: BoundingBox = Field(..., description="Bounding box on viewport")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Perception detection confidence")
    interactive: bool = Field(default=True, description="Whether element is interactive")
    sensitive: bool = Field(default=False, description="Whether element targets sensitive action")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional element properties")



class TextRegion(BaseModel):
    id: str = Field(..., description="Unique text region ID")
    text: str = Field(..., description="Extracted OCR text")
    bbox: BoundingBox = Field(..., description="Bounding box of text region")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class GroundingTarget(BaseModel):
    element_id: str
    element_type: str
    description: str
    bounding_box: BoundingBox
    confidence: float = Field(..., ge=0.0, le=1.0)
    requires_approval: bool = False
    warning: Optional[str] = None


class PerceptionResult(BaseModel):
    screenshot_id: str
    viewport: Dict[str, int] = Field(default_factory=lambda: {"width": 1280, "height": 800})
    elements: List[VisualElement] = Field(default_factory=list)
    text_regions: List[TextRegion] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    warnings: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
