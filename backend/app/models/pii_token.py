from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.company import Company

class PIIToken(Base):
    __tablename__ = "pii_token"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("company.id"), nullable=False, index=True)
    hmac_token: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)  # e.g., HMAC_CUST_8821
    entity_category: Mapped[str] = mapped_column(String(30), nullable=False)  # PIICategory
    original_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 of original value
    display_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # For client-side re-hydration
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship(back_populates="pii_tokens")
