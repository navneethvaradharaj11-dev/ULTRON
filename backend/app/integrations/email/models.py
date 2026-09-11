from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EmailMessageModel(BaseModel):
    id: str
    subject: str
    sender: str
    recipient: str
    body: str
    date: str
    is_draft: bool = False
