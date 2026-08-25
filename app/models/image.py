from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ImageRecord(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    subject: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    attributes: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    caption: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    needs_review: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    embedding: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )