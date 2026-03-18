from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ShortURL(Base):
    __tablename__ = "short_urls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    short_code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    click_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    click_events: Mapped[list["ClickEvent"]] = relationship(
        "ClickEvent", back_populates="short_url", cascade="all, delete-orphan"
    )


class ClickEvent(Base):
    __tablename__ = "click_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    short_code: Mapped[str] = mapped_column(
        String(16), ForeignKey("short_urls.short_code", ondelete="CASCADE"), nullable=False
    )
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    referer: Mapped[str | None] = mapped_column(Text, nullable=True)

    short_url: Mapped["ShortURL"] = relationship("ShortURL", back_populates="click_events")
