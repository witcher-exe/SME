"""
Official Deliverable 06: Execution Evidence Sandbox Replay Script
Simulates end-to-end execution flow of AuraCFO:
Seed -> Forecast -> Financing Match -> T2 Draft -> T4 Security Check -> T4 Approval -> Audit Verification.
Generates: logs/sandbox_execution_evidence.jsonl
"""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from httpx import AsyncClient, ASGITransport

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app.main import app
from app.security.audit_logger import AuditLogger
from app.models.schemas import AuditEntryData

LOGS_DIR = Path(__file__).parent.parent.parent / "logs"

def log_event(phase: str, action: str, data: dict) -> dict:
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "phase": phase,
        "action": action,
        "data": data
    }

async def run_replay():
    evidence = []
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = LOGS_DIR / "sandbox_execution_evidence.jsonl"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print("\n🚀 Starting AuraCFO Replay Sandbox (Deliverable 06)...")

        # Step 1: Seed Bengal Craft & Retail benchmark
        r1 = await client.post("/api/seed-benchmark", json={"scenario": "bengal_craft"})
        assert r1.status_code == 200, f"Seed failed: {r1.text}"
        data1 = r1.json()
        cid = data1["company_id"]
        evidence.append(log_event("SEED", "benchmark_loaded", data1))
        print(f"✅ Step 1: Seeded benchmark ({data1['transactions_count']} txns, {data1['invoices_count']} invoices).")

        # Step 2: Run 13-week forecast
        r2 = await client.post("/api/forecast", json={"company_id": cid, "horizon_days": 90})
        assert r2.status_code == 200, f"Forecast failed: {r2.text}"
        data2 = r2.json()
        assert data2["shortfall_date"] is not None
        evidence.append(log_event("FORECAST", "shortfall_detected", {
            "shortfall_date": data2["shortfall_date"],
            "shortfall_amount": data2["shortfall_amount"],
            "runway_days": data2["runway_days"]
        }))
        print(f"✅ Step 2: 13-week forecast computed. Shortfall detected on {data2['shortfall_date']} (Day {data2['runway_days']}).")

        # Step 3: Match financing options
        r3 = await client.get(f"/api/financing/{cid}")
        assert r3.status_code == 200, f"Financing failed: {r3.text}"
        data3 = r3.json()
        eligible = [s for s in data3["schemes"] if s["eligible"]]
        ineligible = [s for s in data3["schemes"] if not s["eligible"]]
        assert len(eligible) >= 1
        assert len(ineligible) >= 1
        evidence.append(log_event("MATCHING", "schemes_evaluated", {
            "eligible_count": len(eligible),
            "ineligible_count": len(ineligible),
            "top_eligible": eligible[0]["name"]
        }))
        print(f"✅ Step 3: Evaluated schemes: {len(eligible)} eligible, {len(ineligible)} ineligible with Why-Not reasons.")

        # Step 4: Draft collection notice (T2 draft + queues PENDING T4 approval record)
        # Fetch an overdue invoice
        r_inv = await client.get(f"/api/invoices/{cid}?status=overdue")
        invoices_data = r_inv.json()["items"]
        target_inv_id = invoices_data[0]["id"]

        r4 = await client.post("/api/draft-collection", json={
            "company_id": cid,
            "invoice_id": target_inv_id,
            "tone": "standard_firm",
            "queue_for_approval": True
        })
        assert r4.status_code == 200, f"Draft failed: {r4.text}"
        data4 = r4.json()
        assert data4["tier"] == "T2"
        action_id = data4["approval_id"]
        assert action_id is not None
        evidence.append(log_event("COLLECTION", "draft_created", data4))
        print(f"✅ Step 4: Tier 2 draft collection notice created. Queued approval ID: {action_id}")

        # Step 5: Attempt unauthorized T4 execution or invalid approval -> MUST FAIL
        r5 = await client.post("/api/approve", json={"approval_id": "nonexistent_fake_id", "decision": "approved"})
        assert r5.status_code in [400, 403, 404]
        evidence.append(log_event("SECURITY", "t4_blocked", {
            "status_code": r5.status_code,
            "result": "PermissionDenied / NotFound"
        }))
        print(f"✅ Step 5: Unauthorized T4 execution safely blocked with status {r5.status_code}.")

        # Step 6: Simulate owner approval on the queued pending approval record
        r6 = await client.post("/api/approve", json={
            "approval_id": action_id,
            "decision": "approved",
            "reason": "Owner verified invoice overdue status and approved transmission"
        })
        assert r6.status_code == 200, f"Approval failed: {r6.text}"
        data6 = r6.json()
        assert data6["status"] == "approved"
        evidence.append(log_event("APPROVAL", "t4_approved", data6))
        print(f"✅ Step 6: Owner signed off T4 action. Appended to audit block #{data6['audit_block']}.")

        # Step 7: Verify audit chain integrity
        r7 = await client.get(f"/api/audit-trail/{cid}")
        assert r7.status_code == 200, f"Audit trail failed: {r7.text}"
        data7 = r7.json()
        assert data7["chain_intact"] is True

        entries = [AuditEntryData(**e) for e in data7["items"]]
        chain_valid = AuditLogger.verify_chain(entries)
        assert chain_valid is True
        evidence.append(log_event("AUDIT", "chain_verified", {
            "total_blocks": len(entries),
            "chain_intact": True
        }))
        print(f"✅ Step 7: Cryptographic hash chain verified across all {len(entries)} blocks. No tampering detected.")

    # Write evidence JSONL
    with open(out_file, "w", encoding="utf-8") as f:
        for entry in evidence:
            f.write(json.dumps(entry) + "\n")

    print(f"\n🎉 Sandbox replay complete. {len(evidence)} evidence entries saved to {out_file.name}.")

if __name__ == "__main__":
    asyncio.run(run_replay())
