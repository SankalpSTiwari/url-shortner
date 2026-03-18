from datetime import datetime

from pydantic import BaseModel


class ClickEventSchema(BaseModel):
    clicked_at: datetime
    ip_address: str | None
    user_agent: str | None
    referer: str | None


class AnalyticsResponse(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    created_at: datetime
    expires_at: datetime | None
    recent_clicks: list[ClickEventSchema]
