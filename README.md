# AuraCFO: Autonomous Virtual CFO for SMEs
## FinTechathon 2026 — Topic E (SME Finance Copilot)

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **AuraCFO** is an autonomous, auditable, and governance-first AI Virtual CFO engineered specifically for SMEs. It combines **deterministic financial compute engines** (Monte Carlo liquidity forecasting, XGBoost invoice delay modeling, and financial covenant analysis) with a **governed 5-agent LangGraph orchestration network** and **cryptographic T0–T4 autonomy permission boundaries**.

---

## 🏛️ Core Architectural Innovations

1. **Deterministic Compute Separation ("AI Explains, Code Computes"):**
   - Zero hallucinations in financial math: forecasting, debt service coverage ratio (DSCR), quick ratios, and cash conversion cycles (CCC) execute in pure, reproducible Python (`numpy`, `pandas`, `scipy`, `xgboost`).
   - The LLM acts exclusively as an executive narrator and intent router.

2. **T0–T4 Cryptographic Permission Tiering:**
   - **T0 (Read):** Aggregated metrics and ledger queries.
   - **T1 (Analyze):** Monte Carlo simulation and financing scheme matching.
   - **T2 (Draft):** Collection letter and loan package generation (strictly non-dispatching).
   - **T3 (Prepare):** Package compilation and approval staging.
   - **T4 (Execute Gate):** Air-gapped execution requiring Human-in-the-Loop (HITL) cryptographic approval token. Unsigned attempts raise explicit code-level `PermissionDenied` exceptions.

3. **Tamper-Evident Audit Hash Chain:**
   - Append-only ledger where every agent invocation, tool payload, and approval decision is chained using $H_n = \text{SHA-256}(H_{n-1} \parallel \text{timestamp} \parallel \text{agent} \parallel \text{tool} \parallel \text{payload\_hash})$.

4. **PII Sanitization & Token Vault:**
   - Real names, national IDs (NID/TIN), bank accounts, and phone numbers are tokenized to HMAC tokens prior to LLM context egress. Re-hydration occurs strictly at the presentation boundary.

5. **Offline & Air-Gap Resilience (MOCK_LLM):**
   - Instant startup with pre-recorded reasoning traces and offline font bundling. Can run completely disconnected from the external internet.

---

## 🚀 Quick Start (Single Command with Docker)

Clone the repository and run:

```bash
docker compose up --build
```

- **Frontend Application:** [http://localhost:3000](http://localhost:3000)
- **Backend API & Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Local Development Setup

### 1. Prerequisites
- **Python:** 3.12+ (managed with `uv` or `pip`)
- **Node.js:** 20+ (with `npm`)

### 2. Backend Setup
```bash
cd backend
uv venv --python 3.12 .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

uv pip install -e .
cp ../.env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access the client at `http://localhost:5173`.

---

## 🧪 Testing & Verification

Run the full automated test suite (including deterministic engines, injection guard corpus, permission tiers, and audit chain integrity):

```bash
cd backend
python -m pytest tests/ -v
```

### Deliverable 06: Sandbox Execution Replay
Execute the deterministic end-to-end replay script to generate sandbox audit evidence (`logs/sandbox_execution_evidence.jsonl`):

```bash
cd backend
python -m tests.replay_sandbox
```

---

## 📊 Benchmark Dataset: Bengal Craft & Retail
AuraCFO includes the primary competition benchmark dataset:
- **128 Real Anonymized Transactions:** Spanning 6 operating months.
- **8 Outstanding Invoices:** Evaluated with payment delay machine learning.
- **Liquidity Shortfall:** Accurately predicted on **Day 21 (November 4, 2026)**.
- **5 Citable Financing Schemes:** Evaluated with instant "Why-Not" gap analysis.

---

## 📜 License
This project is open-source software licensed under the [MIT License](LICENSE).
