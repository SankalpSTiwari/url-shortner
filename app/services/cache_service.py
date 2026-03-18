import json
from datetime import datetime, timezone

import redis.asyncio as aioredis


CACHE_KEY_PREFIX = "url:"
DEFAULT_TTL = 86400  # 24 hours


def _cache_key(short_code: str) -> str:
    return f"{CACHE_KEY_PREFIX}{short_code}"


async def get_cached_url(redis: aioredis.Redis, short_code: str) -> dict | None:
    raw = await redis.get(_cache_key(short_code))
    if raw is None:
        return None
    return json.loads(raw)


async def set_cached_url(
    redis: aioredis.Redis,
    short_code: str,
    original_url: str,
    expires_at: datetime | None,
) -> None:
    payload = {
        "original_url": original_url,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }
    ttl: int
    if expires_at is None:
        ttl = DEFAULT_TTL
    else:
        remaining = int((expires_at - datetime.now(timezone.utc)).total_seconds())
        ttl = max(1, remaining)

    await redis.set(_cache_key(short_code), json.dumps(payload), ex=ttl)


async def invalidate_cached_url(redis: aioredis.Redis, short_code: str) -> None:
    await redis.delete(_cache_key(short_code))
