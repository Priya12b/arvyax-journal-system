from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    ambience = Column(String, index=True)
    text = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    emotion = Column(String, nullable=True)
    keywords = Column(String, nullable=True)  
    summary = Column(Text, nullable=True)