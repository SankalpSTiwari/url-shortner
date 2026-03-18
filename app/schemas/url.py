from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field


class ShortenRequest(BaseModel):
    original_url: AnyHttpUrl
    custom_alias: str | None = Field(default=None, min_length=3, max_length=16)
    ttl_seconds: int | None = Field(default=None, gt=0)


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    expires_at: datetime | None
    created_at: datetime
