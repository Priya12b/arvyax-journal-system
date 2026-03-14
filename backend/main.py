import os
import json
import sqlite3
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from collections import Counter

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("GEMINI_API_KEY")

def init_db():
    conn = sqlite3.connect("journal.db")
    curr = conn.cursor()
    curr.execute('''CREATE TABLE IF NOT EXISTS entries 
                 (id INTEGER PRIMARY KEY, userId TEXT, ambience TEXT, text TEXT, emotion TEXT, keywords TEXT, summary TEXT)''')
    conn.commit()
    conn.close()

init_db()

class JournalEntry(BaseModel):
    userId: str
    ambience: str
    text: str

@app.post("/api/journal")
async def create_entry(entry: JournalEntry):
    conn = sqlite3.connect("journal.db")
    curr = conn.cursor()
    curr.execute("INSERT INTO entries (userId, ambience, text) VALUES (?, ?, ?)", 
                 (entry.userId, entry.ambience, entry.text))
    entry_id = curr.lastrowid
    conn.commit()
    conn.close()
    return {"id": entry_id, "status": "success"}

@app.get("/api/journal/{userId}")
async def get_entries(userId: str):
    conn = sqlite3.connect("journal.db")
    curr = conn.cursor()
    curr.execute("SELECT ambience, text, emotion FROM entries WHERE userId=?", (userId,))
    rows = curr.fetchall()
    conn.close()
    return [{"ambience": r[0], "text": r[1], "emotion": r[2]} for r in rows]

@app.post("/api/journal/analyze")
async def analyze_emotion(data: dict):
    entry_id = data.get("entryId")  
    text = data.get("text", "")
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        parsed_result = {"emotion": "Calm", "keywords": ["nature", "peace"], "summary": "User feels a sense of relaxation."}
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": f"Analyze the emotion of this journal entry: '{text}'. Return ONLY a JSON object with keys 'emotion' (string), 'keywords' (list), and 'summary' (string). Do not include markdown formatting."}]
            }]
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            
            raw_text = result['candidates'][0]['content']['parts'][0]['text']
            
            clean_json = raw_text.replace("```json", "").replace("```", "").strip()
            
            parsed_result = json.loads(clean_json)
        except Exception as e:
            print(f"Detailed Error: {e}")
            parsed_result = {
                "emotion": "Reflective", 
                "keywords": ["journal", "thoughtful"], 
                "summary": "The system processed the entry and noted a reflective state."
            }
    
    conn = sqlite3.connect("journal.db")
    curr = conn.cursor()
    curr.execute("UPDATE entries SET emotion=?, keywords=?, summary=? WHERE id=?", 
                 (parsed_result["emotion"], json.dumps(parsed_result["keywords"]), parsed_result["summary"], entry_id))
    conn.commit()
    conn.close()
    
    return parsed_result
    
@app.get("/api/journal/insights/{userId}")
async def get_insights(userId: str):
    conn = sqlite3.connect("journal.db")
    curr = conn.cursor()
    curr.execute("SELECT ambience, emotion, keywords FROM entries WHERE userId=?", (userId,))
    rows = curr.fetchall()
    conn.close()
    
    if not rows:
        return {"totalEntries": 0, "topEmotion": None, "mostUsedAmbience": None, "recentKeywords": []}
    
    total_entries = len(rows)
    
    ambiences = [r[0] for r in rows]
    emotions = [r[1] for r in rows if r[1]]
    keywords = []
    for r in rows:
        if r[2]:
            keywords.extend(json.loads(r[2]))
    
    top_emotion = Counter(emotions).most_common(1)[0][0] if emotions else None
    most_used_ambience = Counter(ambiences).most_common(1)[0][0] if ambiences else None
    recent_keywords = list(dict.fromkeys(keywords[::-1]))[:5]
    
    return {
        "totalEntries": total_entries,
        "topEmotion": top_emotion,
        "mostUsedAmbience": most_used_ambience,
        "recentKeywords": recent_keywords
    }