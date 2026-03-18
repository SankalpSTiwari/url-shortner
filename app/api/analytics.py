from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics_service import get_analytics

router = APIRouter()


@router.get("/{short_code}", response_model=AnalyticsResponse)
async def get_url_analytics(
    short_code: str,
    db: AsyncSession = Depends(get_db),
):
    data = await get_analytics(db, short_code)
    if data is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return AnalyticsResponse(**data)
