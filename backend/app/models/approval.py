from datetime import datetime
from typing import TYPE_CHECKING, Optional, Any, Dict
from sqlalchemy import String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.company import Company

class Approval(Base):
    __tablename__ = "approval"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("company.id"), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)  # ApprovalActionType
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)  # Full action details
    justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Agent's justification
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # ApprovalStatus
    requested_by: Mapped[str] = mapped_column(String(50), nullable=False)  # Agent role
    approved_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "owner" or null
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approval_token: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # Cryptographic token
    thread_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # LangGraph thread_id for resuming interrupt()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    company: Mapped["Company"] = relationship(back_populates="approvals")
