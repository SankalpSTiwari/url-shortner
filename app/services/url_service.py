from datetime import datetime, timedelta, timezone

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AliasConflictError, URLExpiredError, URLNotFoundError
from app.db.models import ShortURL
from app.services.cache_service import get_cached_url, invalidate_cached_url, set_cached_url
from app.services.shortener import base62_encode, validate_custom_alias


async def create_short_url(
    session: AsyncSession,
    redis: aioredis.Redis,
    original_url: str,
    custom_alias: str | None = None,
    ttl_seconds: int | None = None,
) -> ShortURL:
    expires_at: datetime | None = None
    if ttl_seconds is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

    if custom_alias is not None:
        if not validate_custom_alias(custom_alias):
            raise ValueError(
                "Custom alias must be 3-16 characters and contain only letters, digits, _ or -"
            )
        url = ShortURL(
            short_code=custom_alias,
            original_url=original_url,
            is_custom=True,
            expires_at=expires_at,
        )
        session.add(url)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise AliasConflictError(custom_alias)
    else:
        # Two-step write: insert placeholder, then update with base62(id)
        url = ShortURL(
            short_code="PLACEHOLDER",
            original_url=original_url,
            is_custom=False,
            expires_at=expires_at,
        )
        session.add(url)
        await session.flush()  # get id without committing
        short_code = base62_encode(url.id)
        url.short_code = short_code
        await session.commit()

    await set_cached_url(redis, url.short_code, url.original_url, url.expires_at)
    return url


async def resolve_short_url(
    session: AsyncSession,
    redis: aioredis.Redis,
    short_code: str,
) -> str:
    cached = await get_cached_url(redis, short_code)
    if cached is not None:
        expires_at_str = cached.get("expires_at")
        if expires_at_str is not None:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now(timezone.utc) > expires_at:
                raise URLExpiredError(short_code)
        return cached["original_url"]

    result = await session.execute(
        select(ShortURL).where(ShortURL.short_code == short_code)
    )
    url = result.scalar_one_or_none()
    if url is None:
        raise URLNotFoundError(short_code)

    if url.expires_at is not None and datetime.now(timezone.utc) > url.expires_at:
        raise URLExpiredError(short_code)

    await set_cached_url(redis, short_code, url.original_url, url.expires_at)
    return url.original_url


async def delete_short_url(
    session: AsyncSession,
    redis: aioredis.Redis,
    short_code: str,
) -> None:
    result = await session.execute(
        select(ShortURL).where(ShortURL.short_code == short_code)
    )
    url = result.scalar_one_or_none()
    if url is None:
        raise URLNotFoundError(short_code)

    await session.delete(url)
    await session.commit()
    await invalidate_cached_url(redis, short_code)
