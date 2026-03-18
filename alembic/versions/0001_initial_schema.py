"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-17 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "short_urls",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("short_code", sa.String(length=16), nullable=False),
        sa.Column("original_url", sa.Text(), nullable=False),
        sa.Column("is_custom", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("click_count", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("short_code"),
    )
    op.create_index(
        "ix_short_urls_expires_at",
        "short_urls",
        ["expires_at"],
        postgresql_where=sa.text("expires_at IS NOT NULL"),
    )

    op.create_table(
        "click_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("short_code", sa.String(length=16), nullable=False),
        sa.Column(
            "clicked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("referer", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["short_code"], ["short_urls.short_code"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_click_events_short_code", "click_events", ["short_code"])
    op.create_index("ix_click_events_clicked_at", "click_events", ["clicked_at"])


def downgrade() -> None:
    op.drop_table("click_events")
    op.drop_table("short_urls")
