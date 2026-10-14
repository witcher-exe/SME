from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Float, DateTime, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.company import Company

class Invoice(Base):
    __tablename__ = "invoice"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("company.id"), nullable=False, index=True)
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False)
    debtor_name: Mapped[str] = mapped_column(String(255), nullable=False)  # HMAC token if PII
    debtor_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    paid_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="issued")  # InvoiceStatus enum
    p_delay: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0.0 to 1.0 probability of late payment
    predicted_delay_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # RiskLevel enum
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship(back_populates="invoices")
