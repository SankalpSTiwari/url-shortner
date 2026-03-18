from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import ClickEvent, ShortURL


async def record_click(
    short_code: str,
    ip_address: str | None,
    user_agent: str | None,
    referer: str | None,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        async with session.begin():
            event = ClickEvent(
                short_code=short_code,
                ip_address=ip_address,
                user_agent=user_agent,
                referer=referer,
            )
            session.add(event)
            await session.execute(
                update(ShortURL)
                .where(ShortURL.short_code == short_code)
                .values(click_count=ShortURL.click_count + 1)
            )


async def get_analytics(session: AsyncSession, short_code: str) -> dict | None:
    result = await session.execute(
        select(ShortURL).where(ShortURL.short_code == short_code)
    )
    url = result.scalar_one_or_none()
    if url is None:
        return None

    events_result = await session.execute(
        select(ClickEvent)
        .where(ClickEvent.short_code == short_code)
        .order_by(ClickEvent.clicked_at.desc())
        .limit(100)
    )
    events = events_result.scalars().all()

    return {
        "short_code": url.short_code,
        "original_url": url.original_url,
        "click_count": url.click_count,
        "created_at": url.created_at,
        "expires_at": url.expires_at,
        "recent_clicks": [
            {
                "clicked_at": e.clicked_at,
                "ip_address": e.ip_address,
                "user_agent": e.user_agent,
                "referer": e.referer,
            }
            for e in events
        ],
    }
