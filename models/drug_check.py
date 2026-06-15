import uuid

from sqlalchemy import String, DateTime, ForeignKey, func, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class DrugCheck(Base):
    __tablename__ = "drug_checks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    visitor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("visitors.id"), nullable=False, index=True
    )
    drugs: Mapped[dict] = mapped_column(JSON, nullable=False)
    analysis: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
