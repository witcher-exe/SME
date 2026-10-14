import csv
import hashlib
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List
import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models.company import Company
from app.models.transaction import Transaction
from app.models.invoice import Invoice
from app.models.audit_entry import AuditEntry
from app.models.pii_token import PIIToken
from app.models.enums import BenchmarkScenario, InvoiceStatus, RiskLevel, Direction, PIICategory
from app.models.schemas import SeedBenchmarkResponse
from app.security.pii_sanitizer import PIISanitizer
from app.security.audit_logger import AuditLogger

DATA_DIR = Path(__file__).parent.parent.parent / "data"

class BenchmarkService:
    """Service to load pre-built benchmark datasets into the database with full PII scrubbing and audit logging."""

    @classmethod
    async def seed_scenario(
        cls,
        session_factory: async_sessionmaker[AsyncSession],
        scenario: BenchmarkScenario = BenchmarkScenario.BENGAL_CRAFT
    ) -> SeedBenchmarkResponse:
        async with session_factory() as session:
            scenario_val = scenario.value if hasattr(scenario, "value") else str(scenario)
            if scenario_val == BenchmarkScenario.BENGAL_CRAFT.value:
                return await cls._seed_bengal_craft(session)
            elif scenario_val == BenchmarkScenario.SHENZHEN_IMPORTER.value:
                return await cls._seed_shenzhen_importer(session)
            else:
                raise ValueError(f"Unknown benchmark scenario: {scenario}")

    @classmethod
    async def _seed_bengal_craft(cls, session: AsyncSession) -> SeedBenchmarkResponse:
        company_id = "bengal-craft-retail-uuid-001"
        company_name = "Bengal Craft & Retail"
        currency = "BDT"
        industry = "Retail & Handicrafts"
        initial_cash_balance = 450000.00
        owner_name_hash = hashlib.sha256("Md. Rafiqul Islam".encode("utf-8")).hexdigest()
        tax_id_hash = hashlib.sha256("TIN-8899-7711-22".encode("utf-8")).hexdigest()

        # Idempotency: Clean existing company and related data
        existing = await session.execute(select(Company).where(Company.id == company_id))
        if existing.scalar_one_or_none():
            await session.execute(delete(Transaction).where(Transaction.company_id == company_id))
            await session.execute(delete(Invoice).where(Invoice.company_id == company_id))
            await session.execute(delete(AuditEntry).where(AuditEntry.company_id == company_id))
            await session.execute(delete(PIIToken).where(PIIToken.company_id == company_id))
            await session.execute(delete(Company).where(Company.id == company_id))
            await session.commit()

        # Create Company with balance sheet snapshot for covenant & CCC math
        company = Company(
            id=company_id,
            name=company_name,
            currency=currency,
            industry=industry,
            owner_name_hash=owner_name_hash,
            tax_id_hash=tax_id_hash,
            initial_cash_balance=initial_cash_balance,
            balance_sheet_snapshot={
                "inventory_bdt": 165000.0,
                "accounts_payable_bdt": 180000.0,
                "current_liabilities_bdt": 320000.0,
                "total_debt_bdt": 450000.0,
                "total_equity_bdt": 280000.0,
                "monthly_debt_service_bdt": 45000.0
            },
            created_at=datetime.utcnow()
        )
        session.add(company)

        # 1. Ingest Transactions
        ledger_path = DATA_DIR / "bengal_craft_ledger.csv"
        pii_tokens_created = 0
        transactions: List[Transaction] = []
        min_date = "2026-10-14"
        max_date = "2026-04-01"

        if ledger_path.exists():
            seen_tokens = set()
            with open(ledger_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_narr = row.get("raw_narration", "")
                    sanitized_narr, narr_redactions = PIISanitizer.sanitize_text(raw_narr)
                    
                    raw_cpty = row.get("counterparty", "")
                    sanitized_cpty, cpty_redactions = PIISanitizer.sanitize_text(raw_cpty)
                    
                    # Store unique PII tokens in DB vault
                    all_redactions = narr_redactions + cpty_redactions
                    for red in all_redactions:
                        if red["token"] not in seen_tokens:
                            seen_tokens.add(red["token"])
                            pii_token_record = PIIToken(
                                id=str(uuid.uuid4()),
                                company_id=company_id,
                                hmac_token=red["token"],
                                entity_category=red["category"],
                                original_hash=red["original_hash"],
                                display_value=red["original"][:2] + "****" + red["original"][-2:] if len(red["original"]) > 4 else "****",
                                created_at=datetime.utcnow()
                            )
                            session.add(pii_token_record)
                            pii_tokens_created += 1

                    txn_date_str = row["date"]
                    if txn_date_str < min_date:
                        min_date = txn_date_str
                    if txn_date_str > max_date:
                        max_date = txn_date_str

                    txn = Transaction(
                        id=row.get("id") or str(uuid.uuid4()),
                        company_id=company_id,
                        date=date.fromisoformat(txn_date_str),
                        amount=float(row["amount"]),
                        direction=row["direction"],
                        category=row.get("category"),
                        counterparty=sanitized_cpty,
                        raw_narration=sanitized_narr,
                        pii_scrubbed=True,
                        created_at=datetime.utcnow()
                    )
                    transactions.append(txn)
                    session.add(txn)

        # 2. Ingest Invoices
        invoices_path = DATA_DIR / "bengal_craft_invoices.csv"
        invoices: List[Invoice] = []
        if invoices_path.exists():
            with open(invoices_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    p_delay = float(row["p_delay"]) if row.get("p_delay") else None
                    pred_days = int(row["predicted_delay_days"]) if row.get("predicted_delay_days") else None
                    paid_date = date.fromisoformat(row["paid_date"]) if row.get("paid_date") else None
                    
                    inv = Invoice(
                        id=row.get("id") or str(uuid.uuid4()),
                        company_id=company_id,
                        invoice_number=row["invoice_number"],
                        debtor_name=row["debtor_name"],
                        debtor_email=row.get("debtor_email"),
                        amount=float(row["amount"]),
                        issued_date=date.fromisoformat(row["issued_date"]),
                        due_date=date.fromisoformat(row["due_date"]),
                        paid_date=paid_date,
                        status=row.get("status", "issued"),
                        p_delay=p_delay,
                        predicted_delay_days=pred_days,
                        risk_level=row.get("risk_level", "low"),
                        created_at=datetime.utcnow()
                    )
                    invoices.append(inv)
                    session.add(inv)

        # 3. Genesis Audit Entry (H_0 chain initiation using AuditLogger.compute_hash)
        prev_hash = "0" * 64
        ts = datetime.utcnow()
        agent = "system"
        tool = "seed_benchmark"
        in_hash = hashlib.sha256("bengal_craft".encode("utf-8")).hexdigest()
        out_hash = hashlib.sha256(f"bengal_craft_{len(transactions)}_{len(invoices)}".encode("utf-8")).hexdigest()
        curr_hash = AuditLogger.compute_hash(prev_hash, ts.isoformat(), agent, tool, in_hash, out_hash)

        genesis_audit = AuditEntry(
            id=str(uuid.uuid4()),
            company_id=company_id,
            block_number=1,
            timestamp=ts,
            agent_role=agent,
            tool_name=tool,
            input_hash=in_hash,
            output_hash=out_hash,
            permission_tier="T0",
            current_hash=curr_hash,
            previous_hash=prev_hash
        )
        session.add(genesis_audit)

        await session.commit()

        return SeedBenchmarkResponse(
            company_id=company_id,
            company_name=company_name,
            transactions_count=len(transactions),
            invoices_count=len(invoices),
            pii_entities_redacted=pii_tokens_created,
            date_range={"start": min_date, "end": max_date},
            initial_cash_balance=initial_cash_balance,
            message="Bengal Craft & Retail loaded successfully."
        )

    @classmethod
    async def _seed_shenzhen_importer(cls, session: AsyncSession) -> SeedBenchmarkResponse:
        company_id = "shenzhen-importer-uuid-002"
        company_name = "Shenzhen Importer Ltd"
        currency = "USD"
        industry = "Consumer Electronics & Cross-Border Trade"
        initial_cash_balance = 120000.00

        # Similar idempotent clean
        existing = await session.execute(select(Company).where(Company.id == company_id))
        if existing.scalar_one_or_none():
            await session.execute(delete(Transaction).where(Transaction.company_id == company_id))
            await session.execute(delete(Invoice).where(Invoice.company_id == company_id))
            await session.execute(delete(AuditEntry).where(AuditEntry.company_id == company_id))
            await session.execute(delete(PIIToken).where(PIIToken.company_id == company_id))
            await session.execute(delete(Company).where(Company.id == company_id))
            await session.commit()

        company = Company(
            id=company_id,
            name=company_name,
            currency=currency,
            industry=industry,
            initial_cash_balance=initial_cash_balance,
            created_at=datetime.utcnow()
        )
        session.add(company)

        csv_path = DATA_DIR / "shenzhen_importer.csv"
        txns: List[Transaction] = []
        min_date = "2026-10-10"
        max_date = "2026-05-01"

        if csv_path.exists():
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    d_str = row["date"]
                    if d_str < min_date: min_date = d_str
                    if d_str > max_date: max_date = d_str
                    txn = Transaction(
                        id=row.get("id") or str(uuid.uuid4()),
                        company_id=company_id,
                        date=date.fromisoformat(d_str),
                        amount=float(row["amount"]),
                        direction=row["direction"],
                        category=row.get("category"),
                        counterparty=row.get("counterparty"),
                        raw_narration=row.get("raw_narration"),
                        pii_scrubbed=True,
                        created_at=datetime.utcnow()
                    )
                    txns.append(txn)
                    session.add(txn)

        await session.commit()

        return SeedBenchmarkResponse(
            company_id=company_id,
            company_name=company_name,
            transactions_count=len(txns),
            invoices_count=0,
            pii_entities_redacted=0,
            date_range={"start": min_date, "end": max_date},
            initial_cash_balance=initial_cash_balance,
            message="Shenzhen Cross-Border Importer loaded successfully."
        )
