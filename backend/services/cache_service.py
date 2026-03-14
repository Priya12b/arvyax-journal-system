import hashlib
import json
import os
from threading import Lock

from cachetools import TTLCache

try:
    import redis
except ImportError:  # pragma: no cover
    redis = None


DEFAULT_CACHE_TTL_SECONDS = int(os.getenv("ANALYSIS_CACHE_TTL_SECONDS", "3600"))
DEFAULT_CACHE_MAXSIZE = int(os.getenv("ANALYSIS_CACHE_MAXSIZE", "1024"))
DEFAULT_CACHE_BACKEND = os.getenv("ANALYSIS_CACHE_BACKEND", "memory").strip().lower()
DEFAULT_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_memory_cache = TTLCache(maxsize=DEFAULT_CACHE_MAXSIZE, ttl=DEFAULT_CACHE_TTL_SECONDS)
_memory_lock = Lock()
_redis_client = None


def _get_redis_client():
    global _redis_client

    if _redis_client is not None:
        return _redis_client
    if DEFAULT_CACHE_BACKEND != "redis" or redis is None:
        return None

    try:
        client = redis.Redis.from_url(DEFAULT_REDIS_URL, decode_responses=True)
        client.ping()
        _redis_client = client
        return _redis_client
    except Exception:
        return None


def _cache_key(text: str) -> str:
    normalized_text = " ".join(text.strip().split())
    text_hash = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
    return f"journal-analysis:{text_hash}"


def get_cached_analysis(text: str):
    key = _cache_key(text)
    redis_client = _get_redis_client()
    if redis_client is not None:
        payload = redis_client.get(key)
        if payload:
            return json.loads(payload)
        return None

    with _memory_lock:
        return _memory_cache.get(key)


def set_cached_analysis(text: str, analysis: dict):
    key = _cache_key(text)
    redis_client = _get_redis_client()
    if redis_client is not None:
        redis_client.setex(key, DEFAULT_CACHE_TTL_SECONDS, json.dumps(analysis))
        return

    with _memory_lock:
        _memory_cache[key] = analysis