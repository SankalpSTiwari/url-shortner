from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.router import api_router
from app.config import settings
from app.db.session import async_engine
from app.dependencies import get_redis_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify connectivity
    async with async_engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    redis = get_redis_pool()
    await redis.ping()
    yield
    # Shutdown
    await async_engine.dispose()
    await redis.aclose()


app = FastAPI(title="URL Shortener", version="1.0.0", lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    db_status = "connected"
    redis_status = "connected"

    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    try:
        redis = get_redis_pool()
        await redis.ping()
    except Exception:
        redis_status = "error"

    return JSONResponse({"status": "ok", "db": db_status, "redis": redis_status})
