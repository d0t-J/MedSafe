import uuid

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class Visitor(Base):
    __tablename__ = "visitors"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
