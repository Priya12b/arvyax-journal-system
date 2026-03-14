# Scalability (100k Users)

- **Database:** Switch from SQLite to PostgreSQL with indexing on userId.
- **Load Balancing:** Deploy the FastAPI app on AWS ECS/Fargate with an Auto Scaling Group.
- **Async Processing:** Move LLM calls to a background worker (Celery) so the API remains responsive.

# Cost Reduction (LLM)

- **Summarization:** Only send long entries to the LLM; use simple sentiment analysis for short ones.
- **Batching:** Analyze multiple entries in one API call if possible.

# Caching

Use Redis to store the hash of a journal entry. If a user submits the same text twice, return the cached analysis instantly without calling the LLM.

# Data Protection

- **Encryption:** Use AES-256 for journal text at rest.
- **Auth:** Implement JWT-based authentication to ensure users can only see their own userId data.