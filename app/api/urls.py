from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

import redis.asyncio as aioredis

from app.config import settings
from app.core.exceptions import AliasConflictError, URLExpiredError, URLNotFoundError
from app.db.session import AsyncSessionLocal
from app.dependencies import get_db, get_redis
from app.schemas.url import ShortenRequest, ShortenResponse
from app.services.analytics_service import record_click
from app.services.url_service import create_short_url, delete_short_url, resolve_short_url

router = APIRouter()


@router.post("/shorten", response_model=ShortenResponse, status_code=201)
async def shorten_url(
    body: ShortenRequest,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    try:
        url = await create_short_url(
            session=db,
            redis=redis,
            original_url=str(body.original_url),
            custom_alias=body.custom_alias,
            ttl_seconds=body.ttl_seconds,
        )
    except AliasConflictError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=str(exc))

    return ShortenResponse(
        short_code=url.short_code,
        short_url=f"{settings.base_url}/api/v1/{url.short_code}",
        original_url=url.original_url,
        expires_at=url.expires_at,
        created_at=url.created_at,
    )


@router.get("/{short_code}")
async def redirect_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    from fastapi import HTTPException

    try:
        original_url = await resolve_short_url(db, redis, short_code)
    except URLNotFoundError:
        raise HTTPException(status_code=404, detail="Short URL not found")
    except URLExpiredError:
        raise HTTPException(status_code=410, detail="Short URL has expired")

    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referer = request.headers.get("referer")

    background_tasks.add_task(
        record_click, short_code, ip, user_agent, referer, AsyncSessionLocal
    )

    return RedirectResponse(url=original_url, status_code=302)


@router.delete("/{short_code}", status_code=204)
async def delete_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    from fastapi import HTTPException

    try:
        await delete_short_url(db, redis, short_code)
    except URLNotFoundError:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return Response(status_code=204)
