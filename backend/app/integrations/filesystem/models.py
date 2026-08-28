from typing import Optional, List
from pydantic import BaseModel


class FileEntryModel(BaseModel):
    filename: str
    filepath: str
    size_bytes: int
    is_directory: bool = False
