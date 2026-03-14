from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models
from ..database import SessionLocal, engine
from ..services.llm_service import analyze_text
import json
from collections import Counter

router = APIRouter(prefix="/api/journal", tags=["journal"])

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=schemas.JournalEntry)
def create_entry(entry: schemas.JournalEntryCreate, db: Session = Depends(get_db)):
    db_entry = models.JournalEntry(
        user_id=entry.userId,
        ambience=entry.ambience,
        text=entry.text,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@router.get("/{userId}", response_model=List[schemas.JournalEntry])
def get_entries(userId: str, db: Session = Depends(get_db)):
    return db.query(models.JournalEntry).filter(models.JournalEntry.user_id == userId).order_by(models.JournalEntry.timestamp.desc()).all()

@router.post("/analyze", response_model=schemas.AnalyzeResponse)
def analyze(entry: schemas.AnalyzeRequest):
    result = analyze_text(entry.text)
    return schemas.AnalyzeResponse(**result)

@router.get("/insights/{userId}")
def insights(userId: str, db: Session = Depends(get_db)):
    entries = db.query(models.JournalEntry).filter(models.JournalEntry.user_id == userId).all()
    if not entries:
        raise HTTPException(status_code=404, detail="No entries found")

    total_entries = len(entries)
    emotions = [e.emotion for e in entries if e.emotion]
    ambience = [e.ambience for e in entries]
    keywords = []
    for e in entries:
        if e.keywords:
            try:
                keywords.extend(json.loads(e.keywords))
            except:
                keywords.extend([k.strip() for k in e.keywords.split(",") if k.strip()])

    top_emotion = Counter(emotions).most_common(1)[0][0] if emotions else None
    most_used_ambience = Counter(ambience).most_common(1)[0][0] if ambience else None
    recent_keywords = list(dict.fromkeys(keywords[::-1]))[:5]  # unique last 5

    return {
        "totalEntries": total_entries,
        "topEmotion": top_emotion,
        "mostUsedAmbience": most_used_ambience,
        "recentKeywords": recent_keywords,
    }