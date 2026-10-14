from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.company import Company

class AuditEntry(Base):
    __tablename__ = "audit_entry"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("company.id"), nullable=False, index=True)
    block_number: Mapped[int] = mapped_column(Integer, nullable=False)  # Sequential per company
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    agent_role: Mapped[str] = mapped_column(String(50), nullable=False)  # orchestrator, quant_modeler, etc.
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)  # forecast_cash, match_financing, etc.
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 of input payload
    output_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 of output payload
    permission_tier: Mapped[str] = mapped_column(String(5), nullable=False)  # T0, T1, T2, T3, T4
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)  # H_n
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # H_{n-1}

    company: Mapped["Company"] = relationship(back_populates="audit_entries")
