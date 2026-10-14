from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.invoice import Invoice
    from app.models.audit_entry import AuditEntry
    from app.models.approval import Approval
    from app.models.pii_token import PIIToken

class Company(Base):
    __tablename__ = "company"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BDT")
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    owner_name_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    tax_id_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    initial_cash_balance: Mapped[float] = mapped_column(Float, default=0.0)
    balance_sheet_snapshot: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False
    )  # Keys: inventory_bdt, accounts_payable_bdt, current_liabilities_bdt, total_debt_bdt, total_equity_bdt, monthly_debt_service_bdt

    # Relationships
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    invoices: Mapped[List["Invoice"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    audit_entries: Mapped[List["AuditEntry"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    approvals: Mapped[List["Approval"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    pii_tokens: Mapped[List["PIIToken"]] = relationship(back_populates="company", cascade="all, delete-orphan")
