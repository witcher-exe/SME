from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Float, DateTime, Date, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.company import Company

class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("company.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # Direction enum: credit / debit
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # revenue, expense, payroll, etc.
    counterparty: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # HMAC token if PII
    raw_narration: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # PII-scrubbed bank narration
    pii_scrubbed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship(back_populates="transactions")
