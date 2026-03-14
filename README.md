# AI-Assisted Journal System (ArvyaX)

ArvyaX users complete immersive nature sessions (forest, ocean, mountain) and then write journal entries. This project stores journal entries, analyzes emotions with an LLM, and provides user-level mental state insights over time.

## Assignment Goal Coverage

This submission covers the required areas:

- API design with FastAPI endpoints for create, fetch, analyze, and insights
- Frontend integration with a simple React interface
- Practical LLM usage for structured emotion analysis output
- Data persistence with SQLite
- Required documentation in README and architecture notes

## Problem Statement

After each ambience session, users write a short reflection. The system should:

- Store journal entries
- Analyze emotion, keywords, and summary using an LLM
- Show aggregate insights per user over time

## Implemented Core Features

### 1. Journal Entry API

#### Create Entry

- Method: `POST`
- Path: `/api/journal`
- Request body:

```json
{
   "userId": "123",
   "ambience": "forest",
   "text": "I felt calm today after listening to the rain."
}
```

- Response example:

```json
{
   "id": 1,
   "status": "success"
}
```

#### Get Entries by User

- Method: `GET`
- Path: `/api/journal/{userId}`
- Response example:

```json
[
   {
      "ambience": "forest",
      "text": "I felt calm today after listening to the rain.",
      "emotion": "Calm"
   }
]
```

### 2. LLM Emotion Analysis API

#### Analyze Entry Text

- Method: `POST`
- Path: `/api/journal/analyze`
- Request body:

```json
{
   "entryId": 1,
   "text": "I felt calm today after listening to the rain"
}
```

Notes:

- `text` is used for analysis.
- `entryId` is used to persist analysis back to the saved entry.

- Response example:

```json
{
   "emotion": "calm",
   "keywords": ["rain", "nature", "peace"],
   "summary": "User experienced relaxation during the forest session"
}
```

### 3. Insights API

#### Get Mental State Insights

- Method: `GET`
- Path: `/api/journal/insights/{userId}`
- Response example:

```json
{
   "totalEntries": 8,
   "topEmotion": "calm",
   "mostUsedAmbience": "forest",
   "recentKeywords": ["focus", "nature", "rain"]
}
```

## Minimal Frontend

One simple React page supports:

- Writing a journal entry
- Viewing previous entries
- Triggering AI analysis per entry
- Viewing user-level insights

## Tech Stack

- Backend: Python + FastAPI
- Frontend: React
- Database: SQLite
- LLM: Google Gemini API

## Bonus Features Implemented

- Caching analysis results (in-memory cache; Redis-compatible cache layer support)
- Rate limiting on API endpoints (SlowAPI)
- Deployment-ready frontend API base URL via environment variable

## Project Structure

```text
arvyax-journal-system/
   backend/
      main.py
      requirements.txt
      services/
         cache_service.py
   frontend/
      src/
         App.js
   README.md
   ARCHITECTURE.md
```

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`.

### 2. Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs at `http://localhost:3000`.

## Environment Variables

Backend `.env` (in `backend/`):

- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`
- `ANALYSIS_CACHE_BACKEND` (`memory` or `redis`)
- `ANALYSIS_CACHE_TTL_SECONDS`
- `REDIS_URL` (if Redis backend is used)
- `LLM_MODEL`
- `PROMPT_VERSION`

Frontend environment variable for deployed setup:

- `REACT_APP_API_BASE_URL` (example: hosted backend URL)

## API Quick Test (curl)

### Create entry

```bash
curl -X POST http://localhost:8000/api/journal \
   -H "Content-Type: application/json" \
   -d '{"userId":"123","ambience":"forest","text":"I felt calm today."}'
```

### Analyze entry

```bash
curl -X POST http://localhost:8000/api/journal/analyze \
   -H "Content-Type: application/json" \
   -d '{"entryId":1,"text":"I felt calm today."}'
```

### Get insights

```bash
curl http://localhost:8000/api/journal/insights/123
```

## Architecture Notes

See `ARCHITECTURE.md` for:

- Scaling strategy to 100k users
- LLM cost optimization strategy
- Cache strategy for repeated analysis
- Sensitive journal data protection strategy

## Deployment

- Backend can be deployed on Render as a Python web service
- Frontend can be deployed on Vercel with `REACT_APP_API_BASE_URL` configured

## Submission Checklist

- [x] README included
- [x] ARCHITECTURE.md included
- [x] Required API endpoints implemented
- [x] Frontend integrated with backend APIs
- [x] LLM analysis returns structured output (emotion, keywords, summary)
