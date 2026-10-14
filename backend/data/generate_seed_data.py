import csv
from datetime import date, timedelta
from pathlib import Path
import random

DATA_DIR = Path(__file__).parent.resolve()

# Set fixed seed for 100% reproducible benchmark data
random.seed(42)

def generate_bengal_craft():
    # 1. Generate 128 transactions from 2026-04-01 to 2026-10-12
    start_date = date(2026, 4, 1)
    end_date = date(2026, 10, 12)
    total_days = (end_date - start_date).days

    customers = [
        ("Acme Corp Bangladesh", "01711002233", "TIN-9821-4412"),
        ("Apex Retailers Ltd", "01819223344", "TIN-7712-3319"),
        ("Dhaka Handloom Emporium", "01912334455", "TIN-5511-9920"),
        ("Bengal Heritage Gift Shop", "01715443322", "TIN-4422-1109"),
        ("Padma Crafts Ltd", "01611889900", "TIN-3321-7788"),
        ("Sylhet Tea & Souvenirs", "01719998877", "TIN-6655-2233"),
        ("POS Merchant Settlement CityBank", "01311223344", "TIN-1122-3344"),
        ("Biman Bangladesh Duty Free", "01811556677", "TIN-9988-7766"),
    ]

    suppliers = [
        ("Dhaka Textiles & Weaving Mill", "supplier_raw_materials"),
        ("Chittagong Jute & Crafts Works", "supplier_raw_materials"),
        ("Sonargaon Brass & Metal Artisans", "supplier_raw_materials"),
        ("Gulshan Showroom Commercial Lease", "rent"),
        ("Dhanmondi Retail Outlet Rent", "rent"),
        ("Staff Monthly Payroll & Wages", "payroll"),
        ("DESCO Commercial Electricity", "utilities"),
        ("Titas Gas Transmission Co", "utilities"),
        ("Sundarban Courier & Logistics", "logistics"),
        ("Paper & Packaging Supplies BD", "supplies"),
        ("Standard Chartered Bank Loan EMI", "loan_emi"),
    ]

    transactions = []

    # Distribution: roughly 70 debits (expenses), 58 credits (revenues) = 128 total
    # Dates spread across 194 days
    step_days = [int(i * (total_days / 128)) for i in range(128)]

    for idx, d_offset in enumerate(step_days):
        txn_date = start_date + timedelta(days=d_offset)
        # 58 credits, 70 debits
        is_credit = idx in [0, 2, 4, 7, 9, 11, 14, 16, 18, 21, 23, 25, 28, 30, 32, 35, 37, 39,
                            42, 44, 46, 49, 51, 53, 56, 58, 60, 63, 65, 67, 70, 72, 74, 77, 79,
                            81, 84, 86, 88, 91, 93, 95, 98, 100, 102, 105, 107, 109, 112, 114,
                            116, 118, 120, 122, 124, 125, 126, 127]

        if is_credit:
            cust, phone, tin = random.choice(customers)
            # Inflows: earlier months healthy, recent months delayed
            if idx > 90:
                amount = round(random.uniform(35000, 65000), 2)
            else:
                amount = round(random.uniform(55000, 85000), 2)
            direction = "credit"
            category = "revenue"
            counterparty = cust
            narration = f"Customer payment received from {cust} Phone: {phone} Ref: {tin}"
        else:
            supp, cat = random.choice(suppliers)
            if cat == "rent":
                amount = round(random.choice([60000, 75000]), 2)
            elif cat == "payroll":
                amount = round(random.choice([95000, 110000]), 2)
            elif cat == "loan_emi":
                amount = 45000.00
            elif cat == "utilities":
                amount = round(random.uniform(10000, 22000), 2)
            else:
                amount = round(random.uniform(40000, 75000), 2)
            direction = "debit"
            category = cat
            counterparty = supp
            narration = f"Bank transfer debit to {supp} on account of {cat} voucher #{1000 + idx}"

        if direction == "debit" and category != "loan_emi":
            amount = round(amount * 0.9354, 2)

        transactions.append({
            "id": f"TXN-2026-{idx+1:04d}",
            "date": txn_date.isoformat(),
            "amount": amount,
            "direction": direction,
            "category": category,
            "counterparty": counterparty,
            "raw_narration": narration,
            "pii_scrubbed": "false"
        })

    # Write bengal_craft_ledger.csv
    with open(DATA_DIR / "bengal_craft_ledger.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "date", "amount", "direction", "category", "counterparty", "raw_narration", "pii_scrubbed"
        ])
        writer.writeheader()
        writer.writerows(transactions)

    # 2. Invoices: 48 historical paid invoices for XGBoost model training + 8 active invoices (56 total)
    invoices = []

    # 48 Historical Settled Invoices
    hist_start = date(2025, 10, 1)
    for h in range(48):
        c_info = customers[h % len(customers)]
        cust_name = c_info[0]
        amt = round(random.uniform(25000, 220000), 2)
        issued = hist_start + timedelta(days=h * 7)
        due = issued + timedelta(days=30)
        
        # Debtor payment delay behavior
        if "Acme" in cust_name or "Handloom" in cust_name:
            actual_delay = random.choice([18, 24, 28, 35, 42])
        elif "Apex" in cust_name or "Heritage" in cust_name:
            actual_delay = random.choice([0, 5, 8, 12, 16])
        else:
            actual_delay = random.choice([0, 0, 2, 4, 7])

        paid = due + timedelta(days=actual_delay)
        p_d = min(0.95, max(0.10, actual_delay / 40.0))
        r_l = "high" if p_d > 0.60 else ("medium" if p_d >= 0.30 else "low")

        invoices.append({
            "id": f"INV-HIST-{h+1:03d}",
            "invoice_number": f"BCR-HIST-{h+1:03d}",
            "debtor_name": cust_name,
            "debtor_email": f"accounts@{cust_name.lower().replace(' ', '')[:8]}.bd",
            "amount": amt,
            "issued_date": issued.isoformat(),
            "due_date": due.isoformat(),
            "paid_date": paid.isoformat(),
            "status": "paid",
            "p_delay": round(p_d, 2),
            "predicted_delay_days": actual_delay,
            "risk_level": r_l
        })

    # 8 Active Invoices for current operations & dashboard
    active_invoices = [
        {
            "id": "INV-2026-001",
            "invoice_number": "BCR-2026-001",
            "debtor_name": "Acme Corp Bangladesh (Md. Karim Ullah)",
            "debtor_email": "accounts@acme-corp.bd",
            "amount": 250000.00,
            "issued_date": "2026-09-25",
            "due_date": "2026-10-25",
            "paid_date": "",
            "status": "issued",
            "p_delay": 0.78,
            "predicted_delay_days": 28,
            "risk_level": "high"
        },
        {
            "id": "INV-2026-002",
            "invoice_number": "BCR-2026-002",
            "debtor_name": "Apex Retailers Ltd (Tariqul Islam)",
            "debtor_email": "finance@apex-retail.bd",
            "amount": 180000.00,
            "issued_date": "2026-09-18",
            "due_date": "2026-10-18",
            "paid_date": "",
            "status": "issued",
            "p_delay": 0.42,
            "predicted_delay_days": 10,
            "risk_level": "medium"
        },
        {
            "id": "INV-2026-003",
            "invoice_number": "BCR-2026-003",
            "debtor_name": "Dhaka Handloom Emporium",
            "debtor_email": "procurement@dhakahandloom.com",
            "amount": 120000.00,
            "issued_date": "2026-09-05",
            "due_date": "2026-10-05",
            "paid_date": "",
            "status": "overdue",
            "p_delay": 0.85,
            "predicted_delay_days": 35,
            "risk_level": "high"
        },
        {
            "id": "INV-2026-004",
            "invoice_number": "BCR-2026-004",
            "debtor_name": "Bengal Heritage Gift Shop",
            "debtor_email": "billing@heritagecrafts.bd",
            "amount": 75000.00,
            "issued_date": "2026-08-28",
            "due_date": "2026-09-28",
            "paid_date": "",
            "status": "overdue",
            "p_delay": 0.65,
            "predicted_delay_days": 22,
            "risk_level": "high"
        },
        {
            "id": "INV-2026-005",
            "invoice_number": "BCR-2026-005",
            "debtor_name": "Padma Crafts Ltd (Nusrat Jahan)",
            "debtor_email": "nusrat@padmacrafts.org",
            "amount": 320000.00,
            "issued_date": "2026-10-02",
            "due_date": "2026-11-02",
            "paid_date": "",
            "status": "issued",
            "p_delay": 0.22,
            "predicted_delay_days": 3,
            "risk_level": "low"
        },
        {
            "id": "INV-2026-006",
            "invoice_number": "BCR-2026-006",
            "debtor_name": "Sylhet Tea & Souvenirs",
            "debtor_email": "info@sylhetteas.bd",
            "amount": 95000.00,
            "issued_date": "2026-10-10",
            "due_date": "2026-11-10",
            "paid_date": "",
            "status": "issued",
            "p_delay": 0.28,
            "predicted_delay_days": 4,
            "risk_level": "low"
        },
        {
            "id": "INV-2026-007",
            "invoice_number": "BCR-2026-007",
            "debtor_name": "Sonali Boutique House",
            "debtor_email": "sonali@boutique.bd",
            "amount": 140000.00,
            "issued_date": "2026-08-15",
            "due_date": "2026-09-15",
            "paid_date": "2026-09-22",
            "status": "paid",
            "p_delay": 0.35,
            "predicted_delay_days": 7,
            "risk_level": "medium"
        },
        {
            "id": "INV-2026-008",
            "invoice_number": "BCR-2026-008",
            "debtor_name": "Jamuna Fair Trade Co",
            "debtor_email": "jamuna@fairtrade.org",
            "amount": 210000.00,
            "issued_date": "2026-08-01",
            "due_date": "2026-08-30",
            "paid_date": "2026-09-08",
            "status": "paid",
            "p_delay": 0.31,
            "predicted_delay_days": 9,
            "risk_level": "medium"
        }
    ]

    invoices.extend(active_invoices)

    with open(DATA_DIR / "bengal_craft_invoices.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "invoice_number", "debtor_name", "debtor_email", "amount",
            "issued_date", "due_date", "paid_date", "status", "p_delay",
            "predicted_delay_days", "risk_level"
        ])
        writer.writeheader()
        writer.writerows(invoices)

def generate_shenzhen_importer():
    start_date = date(2026, 5, 1)
    end_date = date(2026, 10, 10)
    total_days = (end_date - start_date).days

    transactions = []
    for idx in range(60):
        d_offset = int(idx * (total_days / 60))
        txn_date = start_date + timedelta(days=d_offset)
        is_credit = idx % 2 == 0
        if is_credit:
            counterparty = "Shenzhen Consumer Electronics Co Ltd"
            amount = round(random.uniform(50000, 300000), 2)
            direction = "credit"
            category = "revenue"
            narration = f"Export sales remittance from {counterparty} LC #SZ-2026-{idx}"
        else:
            counterparty = "Guangzhou Chip Components Corp"
            amount = round(random.uniform(30000, 220000), 2)
            direction = "debit"
            category = "cogs"
            narration = f"Supplier wire transfer to {counterparty} for component inventory"

        transactions.append({
            "id": f"SZ-TXN-{idx+1:03d}",
            "date": txn_date.isoformat(),
            "amount": amount,
            "direction": direction,
            "category": category,
            "counterparty": counterparty,
            "raw_narration": narration,
            "pii_scrubbed": "false"
        })

    with open(DATA_DIR / "shenzhen_importer.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "date", "amount", "direction", "category", "counterparty", "raw_narration", "pii_scrubbed"
        ])
        writer.writeheader()
        writer.writerows(transactions)

if __name__ == "__main__":
    generate_bengal_craft()
    generate_shenzhen_importer()
    print("Seed CSVs generated successfully.")
