# ARCHITECTURE - AI-Assisted Journal System

This document explains the current architecture and answers the required design questions for scale, cost, caching, and security.

## 1) Current Architecture (Implemented)

### Backend

- Framework: FastAPI
- Entry point: `backend/main.py`
- Data store: SQLite (`journal.db`)
- API style: REST endpoints

Implemented endpoints:

- `POST /api/journal` -> create journal entry
- `GET /api/journal/{userId}` -> fetch entries by user
- `POST /api/journal/analyze` -> LLM emotion analysis (emotion, keywords, summary)
- `GET /api/journal/insights/{userId}` -> aggregate insights over time

### LLM Integration

- Provider: Gemini API
- Behavior: backend sends journal text with a structured prompt and parses JSON response
- Persisted result: `emotion`, `keywords`, and `summary` are written back to database

### Frontend

- Framework: React (single-page UI)
- Features: add entry, view history, analyze entry, view insights
- Deployment-ready API base URL via `REACT_APP_API_BASE_URL`

### Operational Features Already Added

- Caching layer for repeated analysis (`memory` mode currently, Redis-compatible)
- Rate limiting with SlowAPI

## 2) How To Scale This To 100k Users

### Application Layer

- Run multiple FastAPI replicas behind a load balancer (Nginx/ALB)
- Move from single-process deployment to containerized horizontal scaling
- Keep API instances stateless so replicas can scale independently

### Data Layer

- Migrate SQLite to PostgreSQL (managed DB)
- Add indexes on high-traffic query fields:
	- `userId`
	- `timestamp`
- Add pagination for `GET /api/journal/{userId}` for large histories

### Asynchronous Processing

- Offload analysis jobs to a worker queue (Celery/RQ)
- API receives request quickly and returns job status endpoint
- Workers perform LLM calls and update entries asynchronously

### Reliability and Observability

- Add centralized logging and metrics (latency, error rate, cache hit ratio)
- Add health checks and automatic restart policies
- Add circuit breaker/fallback when LLM provider is slow or unavailable

## 3) How To Reduce LLM Cost

### Prompt and Request Optimization

- Keep prompts short and structured
- Truncate or summarize very long journal text before full analysis

### Selective LLM Usage

- For very short/simple entries, use lightweight heuristics first
- Call full LLM analysis only when confidence is low

### Caching and Reuse

- Reuse analysis for repeated or near-duplicate text
- Cache key based on normalized text hash

### Model Strategy

- Use a lower-cost model for routine analysis
- Route only ambiguous/high-value cases to a stronger model

## 4) How Repeated Analysis Is Cached

Current implementation:

- Normalize text and generate SHA-256 hash key
- Check cache before external LLM call
- If key exists, return cached JSON immediately
- If key misses, call LLM, then store result in cache

Backends:

- `memory` cache for local/simple setup
- `redis` cache supported for shared multi-instance deployments

Benefits:

- Lower latency for repeated analysis
- Lower API cost
- Better user experience

## 5) How Sensitive Journal Data Is Protected

### Current Baseline

- Environment variables used for API secrets
- Backend-only LLM key usage (not exposed in frontend)
- CORS configured for API access
- Rate limiting reduces abuse risk

### Recommended Production Hardening

- Add authentication and authorization (JWT)
- Enforce per-user data access checks on all endpoints
- Encrypt data at rest (DB disk encryption; field-level encryption for journal text if needed)
- Enforce HTTPS/TLS everywhere
- Add audit logging for read/write access to sensitive entries
- Add secret rotation policy and avoid committing real keys to source control

## 6) Deployment Blueprint (Demo to Production)

### Demo Deployment

- Backend: Render
- Frontend: Vercel
- Fast to review and easy to reproduce for assignment validation

### Production Evolution

- Containerize backend and workers
- PostgreSQL + Redis managed services
- CDN + WAF in front of frontend/backend
- CI/CD with automated tests and staged rollout

## 7) Design Tradeoffs

- SQLite is simple for assignment/demo but not ideal for high concurrency
- Synchronous analysis is easier to implement but can increase response time
- In-memory cache is simple but resets on restart; Redis is better for shared persistence

## 8) Summary

The implemented architecture satisfies assignment requirements now and includes practical production-oriented improvements (caching and rate limiting). The scale path is clear: move to PostgreSQL, add async workers, use Redis as shared cache, and add strong auth and encryption controls for sensitive journal data.