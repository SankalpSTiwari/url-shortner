from fastapi import APIRouter

from app.api import analytics, urls

api_router = APIRouter()

api_router.include_router(urls.router, tags=["urls"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
