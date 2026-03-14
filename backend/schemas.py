from typing import List, Optional
from pydantic import BaseModel

class JournalEntryCreate(BaseModel):
    userId: str
    ambience: str
    text: str

class JournalEntry(BaseModel):
    id: int
    userId: str
    ambience: str
    text: str
    timestamp: str
    emotion: Optional[str] = None
    keywords: Optional[List[str]] = None
    summary: Optional[str] = None

    class Config:
        orm_mode = True

class AnalyzeRequest(BaseModel):
    text: str

class AnalyzeResponse(BaseModel):
    emotion: str
    keywords: List[str]
    summary: str