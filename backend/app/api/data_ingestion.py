import csv
import io
import uuid
from datetime import datetime, date
from typing import Optional, Union, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db, async_session_factory
from app.models.company import Company
from app.models.transaction import Transaction
from app.models.pii_token import PIIToken
from app.models.enums import BenchmarkScenario, PIICategory
from app.models.schemas import (
    SeedBenchmarkRequest,
    SeedBenchmarkResponse,
    IngestPreviewResponse,
    IngestCommitResponse,
    RedactionPreview,
    ErrorResponse
)
from app.services.benchmark_service import BenchmarkService
from app.security.pii_sanitizer import PIISanitizer

router = APIRouter(tags=["Data Ingestion"])

@router.post(
    "/seed-benchmark",
    response_model=SeedBenchmarkResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def seed_benchmark(request: SeedBenchmarkRequest):
    """
    Tier: T0
    Load pre-built benchmark scenario (e.g., Bengal Craft & Retail).
    Idempotent: Cleans previous data before loading.
    """
    try:
        response = await BenchmarkService.seed_scenario(async_session_factory, request.scenario)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Benchmark seeding failed: {str(e)}"
        )

@router.post(
    "/ingest",
    response_model=Union[IngestPreviewResponse, IngestCommitResponse],
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def ingest_file(
    file: UploadFile = File(...),
    company_name: Optional[str] = Form(None),
    currency: Optional[str] = Form("BDT"),
    commit: bool = Form(False),
    db: AsyncSession = Depends(get_db)
):
    """
    Tier: T0
    Upload and parse CSV statement with live PII redaction preview.
    If commit=False: preview parsed rows and detected redactions without writing to DB.
    If commit=True: commit transactions and company to DB.
    """
    contents = await file.read()
    try:
        decoded = contents.decode("utf-8")
    except UnicodeDecodeError:
        decoded = contents.decode("latin-1")

    reader = csv.DictReader(io.StringIO(decoded))
    rows = list(reader)
    if not rows:
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")

    detected_rows = len(rows)
    sample_rows = rows[:5]
    all_redactions: List[Dict[str, str]] = []

    for r in rows:
        narr = r.get("raw_narration") or r.get("narration") or r.get("description") or ""
        cpty = r.get("counterparty") or r.get("customer") or r.get("vendor") or ""
        _, r1 = PIISanitizer.sanitize_text(narr)
        _, r2 = PIISanitizer.sanitize_text(cpty)
        all_redactions.extend(r1)
        all_redactions.extend(r2)

    sample_redactions = [
        RedactionPreview(
            original=red["original"],
            token=red["token"],
            category=PIICategory(red["category"])
        )
        for red in all_redactions[:5]
    ]

    matched_cols = [c for c in ["date", "amount", "direction", "category", "counterparty", "raw_narration"] if c in rows[0]]
    missing_cols = [c for c in ["date", "amount", "direction"] if c not in rows[0]]

    if not commit:
        return IngestPreviewResponse(
            detected_rows=detected_rows,
            sample_rows=sample_rows,
            pii_redactions_detected=len(all_redactions),
            sample_redactions=sample_redactions,
            columns_matched=matched_cols,
            columns_missing=missing_cols
        )

    # Commit mode
    c_name = company_name or file.filename.split(".")[0]
    cid = str(uuid.uuid4())
    comp = Company(
        id=cid,
        name=c_name,
        currency=currency or "BDT",
        created_at=datetime.utcnow()
    )
    db.add(comp)

    imported_txns = 0
    tokens_created = 0

    for r in rows:
        d_val = r.get("date", date.today().isoformat())
        amt = float(r.get("amount", 0.0))
        direction = r.get("direction", "debit")
        cat = r.get("category", "operating")
        raw_c = r.get("counterparty", "")
        raw_n = r.get("raw_narration") or r.get("narration") or ""

        s_c, c_red = PIISanitizer.sanitize_counterparty(raw_c)
        s_n, n_red = PIISanitizer.sanitize_text(raw_n)

        for red in (n_red + ([c_red] if c_red else [])):
            pt = PIIToken(
                id=str(uuid.uuid4()),
                company_id=cid,
                hmac_token=red["token"],
                entity_category=red["category"],
                original_hash=red["original_hash"],
                display_value=red["original"][:2] + "****" if len(red["original"]) > 2 else "****",
                created_at=datetime.utcnow()
            )
            db.add(pt)
            tokens_created += 1

        txn = Transaction(
            id=str(uuid.uuid4()),
            company_id=cid,
            date=date.fromisoformat(d_val),
            amount=amt,
            direction=direction,
            category=cat,
            counterparty=s_c,
            raw_narration=s_n,
            pii_scrubbed=True,
            created_at=datetime.utcnow()
        )
        db.add(txn)
        imported_txns += 1

    await db.commit()

    return IngestCommitResponse(
        company_id=cid,
        transactions_imported=imported_txns,
        invoices_imported=0,
        pii_tokens_created=tokens_created,
        message=f"Successfully ingested {imported_txns} transactions for {c_name}."
    )
