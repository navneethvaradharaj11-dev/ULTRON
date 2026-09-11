from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CalendarEventModel(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    start_time: str
    end_time: str
    location: Optional[str] = None
    attendees: List[str] = Field(default_factory=list)
    status: str = "confirmed"
