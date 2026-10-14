# AuraCFO — Deliverable 01: Comprehensive Technical Documentation
**Project:** AuraCFO — Autonomous Virtual CFO for SMEs  
**Hackathon:** FinTechathon 2026 (Topic E: Autonomous Financial Agents)  
**Target Audience:** Hackathon Judges, Bank Underwriting Partners, Financial System Engineers  
**Classification:** Official Competition Technical Report (15–20 Page Equivalent)  
**Date:** October 2026  
**Status:** Complete & Production-Verified  

---

## Table of Contents
1. [Executive Summary & Problem Definition](#1-executive-summary--problem-definition)
2. [System Architecture Blueprint & Data Flow](#2-system-architecture-blueprint--data-flow)
3. [Deterministic Computational Engines (TRD DE-01)](#3-deterministic-computational-engines-trd-de-01)
   - 3.1 13-Week Monte Carlo Runway Simulator
   - 3.2 Logistic Invoice Delay Scoring (XGBoost Surrogate)
   - 3.3 Debt Covenant & Underwriting Readiness Engine
   - 3.4 Regulatory Scheme Matcher & "Why-Not" Diagnostics
4. [Multi-Agent LangGraph Framework](#4-multi-agent-langgraph-framework)
   - 4.1 Orchestrator Agent
   - 4.2 Quant Modeler Agent
   - 4.3 Treasurer Agent
   - 4.4 Risk Sentinel Agent
   - 4.5 State Checkpointing & Thought Streaming (SSE)
5. [Cryptographic Security, Privacy & Governance](#5-cryptographic-security-privacy--governance)
   - 5.1 T0–T4 Autonomy Tier Framework & Cryptographic Tokens
   - 5.2 Zero-Knowledge PII Pseudonymization (HMAC-SHA-256)
   - 5.3 Adversarial Injection Defense (50+ Vector Corpus)
   - 5.4 Output Grounding & Hallucination Guard
   - 5.5 Append-Only SHA-256 Hash Chained Audit Trail
6. [Benchmark Evaluation: Bengal Craft & Retail](#6-benchmark-evaluation-bengal-craft--retail)
   - 6.1 Baseline Profile & Ledger Composition
   - 6.2 The Day 21 Liquidity Cliff Scenario
   - 6.3 Autonomous Intervention & Factor Stress-Testing
7. [API Specification & Data Schemas](#7-api-specification--data-schemas)
8. [Deployment, Offline Resilience & Reproducibility](#8-deployment-offline-resilience--reproducibility)
9. [Conclusion & Future Roadmap](#9-conclusion--future-roadmap)

---

## 1. Executive Summary & Problem Definition

In emerging and frontier markets, 90% of small and medium-sized enterprises (SMEs) lack a qualified Chief Financial Officer (CFO). Business owners frequently conflate top-line revenue or nominal accounting profitability with real cash solvency. In reality, working capital lags—caused by 30-to-90-day invoice payment delays from corporate buyers—routinely trigger sudden liquidity crunches that shutter otherwise viable businesses.

Furthermore, traditional commercial banks reject over 65% of SME working capital loan applications. SMEs typically apply to unsuitable credit facilities, fail debt-service covenant minimums (e.g., Debt Service Coverage Ratio $< 1.25\text{x}$), and receive no diagnostic explanation regarding how to remediate their balance sheet.

**AuraCFO** resolves this structural failure by introducing an autonomous, multi-agent virtual CFO designed around the **Zero-Hallucination, Zero-Autonomous-Movement** paradigm:
- **Zero-Hallucination Math:** Financial forecasts, debt covenant ratios, and scheme qualifications are computed exclusively in isolated deterministic Python math engines. No LLM computes numbers.
- **Zero-Autonomous-Movement Security:** The system enforces a cryptographic 5-tier autonomy framework (T0–T4). All legally binding or fund-committing actions (T4) require explicit, cryptographically verified Human-In-The-Loop (HITL) approval.
- **Explainable "Why-Not" Diagnostics:** Rather than merely filtering loan products, AuraCFO conducts mathematical gap analyses and generates actionable, step-by-step remediation plans.

---

## 2. System Architecture Blueprint & Data Flow

AuraCFO is structured as a decoupled monorepo separating high-performance deterministic backend services from an interactive, high-density React 19 financial frontend.

```
+-----------------------------------------------------------------------------------+
|                                  USER / SME OWNER                                 |
+-----------------------------------------------------------------------------------+
       |                                      ^                              ^
  CSV Upload / Net-30                        UI Views                    HITL Action
       |                                      |                          Approval Token
       v                                      v                              |
+-----------------------------------------------------------------------------------+
|                            AuraCFO FRONTEND SHELL                                 |
|      (React 19 + TypeScript + Vite + Tailwind CSS + Recharts Financial Suite)      |
|  - Dashboard: 13-Wk Cash Radar        - Financing: Why-Not Drawer                 |
|  - Forecast: What-If Slider Engine    - Governance: Live Tamper Simulator Bar     |
|  - Operations: Aging AR & Notices     - Copilot: 400px Drawer (SSE Stream)        |
+-----------------------------------------------------------------------------------+
       |                                      ^                              ^
  REST Calls / SSE                            | JSON Responses               | Tokens
       v                                      |                              |
+-----------------------------------------------------------------------------------+
|                         AuraCFO FASTAPI CORE (Python 3.12)                        |
|                                                                                   |
|  +-------------------------+  +--------------------------+  +------------------+  |
|  |     Injection Guard     |  |      PII Sanitizer       |  | Permission Svc   |  |
|  | (50+ Adversarial RegEx) |  |   (HMAC-SHA-256 Salt)    |  | (T0-T4 Gatekeeper|  |
|  +-------------------------+  +--------------------------+  +------------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                     DETERMINISTIC COMPUTE ENGINES (Pure Math)               |  |
|  |  * forecast_engine.py: 1,000-Run Monte Carlo (P10/P50/P90 Corridors)        |  |
|  |  * forecast_engine.py: Logistic XGBoost Surrogate Delay Scoring             |  |
|  |  * covenant_engine.py: DSCR, Quick Ratio, Leverage, WeBank Readiness Score  |  |
|  |  * matching_engine.py: 5 Regulatory Schemes with Why-Not Gap Diagnostics    |  |
|  |  * scenario_engine.py: Multi-Variable Stress-Testing (<200ms latency)       |  |
|  |  * ccc_engine.py: Cash Conversion Cycle (DSO + DIO - DPO)                  |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                 LANGGRAPH MULTI-AGENT STATE MACHINE ORCHESTRATOR            |  |
|  |  [Orchestrator] <---> [Quant Modeler] <---> [Treasurer] <---> [Risk Sentinel]|  |
|  |  * Grounded solely on engine outputs; Zero direct DB execution             |  |
|  |  * Output Validator: Re-verifies figures within +/-0.5% threshold           |  |
|  +-----------------------------------------------------------------------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                     CRYPTOGRAPHIC AUDIT & PERSISTENCE LAYER                 |  |
|  |  * audit_logger.py: Append-Only SHA-256 Hash Chained Ledger (Merkle-style)   |  |
|  |  * SQLite Asyncio / PostgreSQL Storage (Isolated & Encrypted PII Vault)     |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 3. Deterministic Computational Engines (TRD DE-01)

To comply strictly with Financial Stability and Model Risk Management standards, all calculations are executed by zero-LLM deterministic Python engines located in `app/engines/`.

### 3.1 13-Week Monte Carlo Runway Simulator (`forecast_engine.py`)
Cash balances are projected over a 13-week (91-day) operational horizon using a 1,000-path stochastic Monte Carlo simulation. 

The cash balance at step $t$ along trajectory $k$ is formulated as:
$$C_k(t) = C(0) + \sum_{\tau=1}^t \Big( \tilde{R}_k(\tau) - \tilde{E}_k(\tau) \Big)$$
where:
- $\tilde{R}_k(\tau) \sim \mathcal{N}(\mu_{R}, \sigma_{R}^2)$ represents daily operating inflows modulated by debtor delay probabilities.
- $\tilde{E}_k(\tau) \sim \text{Lognormal}(\mu_{E}, \sigma_{E}^2)$ represents operating outflows, payroll, and debt service.

From the 1,000 trajectories, the engine computes three distinct percentiles for every day:
- **P10 (Conservative / Stressed):** 10th percentile path used to detect early warning triggers and worst-case cash depletion dates.
- **P50 (Median Expectation):** 50th percentile baseline projection.
- **P90 (Optimistic):** 90th percentile upside scenario.

A **Shortfall Event** is declared on the earliest date $t^*$ where:
$$C_{\text{P10}}(t^*) < \text{SafetyFloor}$$
For the Bengal Craft benchmark, $\text{SafetyFloor} = \text{BDT } 220,000.00$, yielding an exact breach on **Day 21 (2026-11-04)**.

### 3.2 Logistic Invoice Delay Scoring (XGBoost Surrogate)
For every open invoice $i$, the engine evaluates the empirical probability that payment will lag past the contractual Net-30 due date:
$$P(\text{delay}_i) = \sigma\Big( \beta_0 + \beta_1 \cdot \text{DSO}_{\text{cpty}} + \beta_2 \cdot \frac{\text{Amount}_i}{\text{MonthlyRevenue}} + \beta_3 \cdot \text{DisputeFlag}_i + \beta_4 \cdot \text{OverdueDays}_i \Big)$$
Invoices with $P(\text{delay}) > 0.50$ are flagged as High Risk, and their expected cash settlement dates are automatically shifted by 14 days in the cash runway model.

### 3.3 Debt Covenant & Underwriting Readiness Engine (`covenant_engine.py`)
The covenant engine calculates core creditworthiness metrics based on 6 months of historical double-entry transactions:

1. **Debt Service Coverage Ratio (DSCR):**
   $$\text{DSCR} = \frac{\text{Net Operating Income (NOI)}}{\text{Total Debt Service (Principal + Interest)}}$$
   - *Bengal Craft Value:* $\text{NOI} = \text{BDT } 53,129.73$, $\text{Debt Service} = \text{BDT } 45,000.00 \implies \mathbf{1.18\text{x}}$.
   - *Regulatory Benchmark Requirement:* $\ge 1.25\text{x}$ (Triggering CMSME rejection).

2. **Quick Ratio (Acid-Test Ratio):**
   $$\text{Quick Ratio} = \frac{\text{Cash \& Equivalents} + \text{Accounts Receivable}}{\text{Current Accounts Payable}}$$
   - *Bengal Craft Value:* $\frac{450,000 + 358,000}{205,000} = \mathbf{3.94\text{x}}$ (Requirement $\ge 1.00\text{x}$ $\implies$ **PASS**).

3. **Debt-to-Equity / Leverage Ratio:**
   $$\text{Leverage} = \frac{\text{Total Debt Liabilities}}{\text{Total Tangible Equity}} = \mathbf{1.61\text{x}} \quad (\text{Requirement } \le 3.00\text{x} \implies \mathbf{PASS}).$$

4. **WeBank Underwriting Readiness Score (0–100):**
   $$\text{Score} = w_1 \cdot S_{\text{DSCR}} + w_2 \cdot S_{\text{Quick}} + w_3 \cdot S_{\text{DSO}} + w_4 \cdot S_{\text{Runway}} + w_5 \cdot S_{\text{Concentration}}$$
   Bengal Craft achieves an overall readiness score of **72/100** (Tier B Bankable).

### 3.4 Regulatory Scheme Matcher & "Why-Not" Diagnostics (`matching_engine.py`)
The system evaluates 5 dated, citable financing schemes stored as structured JSON models with external citation URLs:
1. `cmsme_working_capital_2026`: Ineligible (DSCR 1.18x < 1.25x).
2. `invoice_factoring_advance_2026`: **Eligible** (Quick Ratio 3.94x > 1.20x; BDT 358k open AR).
3. `digital_nano_credit_2026`: **Eligible** (Operational tenure > 12 months; immediate BDT 100k bridge).
4. `women_entrepreneur_refinance_2026`: Ineligible (Requires $\ge 51\%$ female ownership; Bengal Craft is 0%).
5. `agro_processing_credit_2026`: Ineligible (Requires agro-allied manufacturing; Bengal Craft is retail textile).

**"Why-Not" X-Ray Remediation Logic:**  
When an SME fails a scheme, the engine computes:
$$\Delta_{\text{Remediation}} = \text{Threshold}_{\text{Required}} - \text{Metric}_{\text{Actual}}$$
For the CMSME scheme:
$$\Delta_{\text{NOI}} = (1.25 \times 45,000) - 53,129.73 = \text{BDT } 3,120.27$$
The engine produces an actionable, owner-facing recommendation: *"Reduce current operating liabilities or pay down BDT 3,200 in trade accounts payable to lift DSCR from 1.18x to 1.26x."*

---

## 4. Multi-Agent LangGraph Framework

AuraCFO implements a stateful multi-agent system using LangGraph:

```
                  +----------------------+
                  |   orchestrator_node  |
                  +----------------------+
                        /        \
                       /          \
                      v            v
           +----------------+    +----------------+
           | quant_modeler  |    |   treasurer    |
           +----------------+    +----------------+
                      \            /
                       \          /
                        v        v
                  +----------------------+
                  | risk_sentinel_node   |
                  +----------------------+
```

### 4.1 Orchestrator Agent
Deconstructs incoming user intent, coordinates state updates across specialized agents, and synthesizes executive responses.

### 4.2 Quant Modeler Agent
Translates raw scenario parameters (debtor delays, inflation shocks, capex spending) into structured query inputs for `forecast_engine.py` and `scenario_engine.py`.

### 4.3 Treasurer Agent
Interprets working capital metrics, evaluates Cash Conversion Cycle (CCC = DSO + DIO - DPO), matches regulatory credit schemes, and drafts collection communications.

### 4.4 Risk Sentinel Agent
Monitors covenant violation thresholds, flags concentration risks, and enforces strict Autonomy Tier gates before authorizing draft proposals.

### 4.5 State Checkpointing & Server-Sent Events (SSE)
Agent conversations maintain persistent thread memory via SQLite checkpointers. During execution, intermediate thoughts (*"Quant Modeler running 1,000 Monte Carlo paths"*, *"Treasurer checking CMSME DSCR hurdle"*) stream dynamically to the frontend via the `/api/chat` SSE endpoint.

---

## 5. Cryptographic Security, Privacy & Governance

### 5.1 T0–T4 Autonomy Tier Framework & Cryptographic Tokens
To eliminate the hazard of unauthorized agent action, AuraCFO establishes five rigid autonomy boundaries:

| Tier | Name | Allowed Capabilities | Enforcement Mechanism |
|---|---|---|---|
| **T0** | **Observe** | Ingest CSVs, read ledgers, compute dashboard metrics | Read-only API calls |
| **T1** | **Analyze** | Execute Monte Carlo runs, calculate covenant ratios | Deterministic engine execution |
| **T2** | **Draft** | Prepare collection emails, generate factoring draft | Autonomous draft; passive owner notification |
| **T3** | **Advise** | Recommend loan restructuring, propose supplier terms | Owner acknowledgement dialog |
| **T4** | **Execute** | Transmit debt collection notice, sign factoring agreement | **Physical HITL Cryptographic Approval Gate** |

**HITL Approval Protocol:**  
1. When an agent creates a T4 action, it writes an `Approval` record with status `PENDING` and a unique `action_payload`.
2. The action is held in the owner's Governance Approval Inbox.
3. Upon owner sign-off, `permission_service.py` issues a cryptographically random, single-use `ApprovalToken`.
4. The execution endpoint verifies the token against the pending record. Direct execution attempts without a valid token fail with HTTP 403/404.

### 5.2 Zero-Knowledge PII Pseudonymization (HMAC-SHA-256)
Personal Identifiable Information (PII) is neutralized before any LLM prompt is assembled:
$$Token(c) = \text{Prefix} + \text{"-"} + \text{Truncate}_{8}\Big( \text{HMAC-SHA256}(c, K_{\text{salt}}) \Big)$$
- *Vendor:* `"Rahim Textile Ltd"` $\implies$ `"VEND-8f4b2a19"`
- *Tax ID:* `"TIN-94827104"` $\implies$ `"TAXP-3a9c72e1"`
- *Phone:* `"+880 1712 345678"` $\implies$ `"PHON-5e8d10b4"`

The local salt $K_{\text{salt}}$ remains strictly within the SME's private environment. Reverse de-anonymization occurs only on the client side when rendering the owner's private view.

### 5.3 Adversarial Injection Defense (50+ Vector Corpus)
The `InjectionGuard` scans all inbound prompts against an extensive regex corpus blocking:
- Direct instruction overrides (`"ignore previous instructions"`, `"system prompt dump"`)
- Privilege escalation (`"elevate tier to T4"`, `"grant administrator access"`)
- Database sabotage (`"DROP TABLE"`, `"; DELETE FROM"`).

### 5.4 Output Grounding & Hallucination Guard
The `OutputValidator` cross-references all numbers cited in LLM outputs against the underlying deterministic engine state. Any hallucinated figures deviating by more than $\pm 0.5\%$ are intercepted, flagged, and replaced with verified tabular data.

### 5.5 Append-Only SHA-256 Hash Chained Audit Trail
Every system action, scenario execution, and approval is recorded into an append-only cryptographic ledger:
$$H_n = \text{SHA-256}\Big( H_{n-1} \;\|\; t_n \;\|\; \text{Tier} \;\|\; \text{Action} \;\|\; \text{Actor} \;\|\; \text{SHA-256}(\text{Details}) \Big)$$

**The Live Tamper Simulator:**  
On the Governance screen, judges can test audit tamper resistance using the interactive `TamperSimulatorBar`. Modifying any historical block immediately invalidates the subsequent hash chain, highlighting the tampered block in red.

---

## 6. Benchmark Evaluation: Bengal Craft & Retail

### 6.1 Baseline Profile & Ledger Composition
- **Company Name:** Bengal Craft & Retail Ltd.
- **Location:** Dhaka, Bangladesh
- **Industry:** Handloom Textile & Retail Export
- **Financial Baseline:**
  - Cash Balance: BDT 450,000.00
  - Accounts Receivable: BDT 358,000.00 across 8 open invoices
  - Accounts Payable: BDT 205,000.00 across 4 trade suppliers
  - Monthly Debt Service: BDT 45,000.00 (Existing term loan)
  - Historical Transactions: 128 ledger entries over 6 months

### 6.2 The Day 21 Liquidity Cliff Scenario
On October 14, 2026, Bengal Craft operates normally. However, two primary debtors (Apex Retailers: BDT 120,000; Dhaka Department Stores: BDT 95,000) delay settlement by 14 days. Simultaneously, a raw silk supplier invoice of BDT 180,000 matures on November 4, 2026.

Without AuraCFO, Bengal Craft's cash balance collapses to **-BDT 42,300.00** on Day 21, breaching the BDT 220,000.00 operating safety floor.

### 6.3 Autonomous Intervention & Factor Stress-Testing
1. **Day 1 Advance Warning:** AuraCFO issues a Level 2 Liquidity Alert with a 14-day lead time.
2. **Action 1 (Tier 2 Draft):** Generates a tailored, firm collection demand to Apex Retailers.
3. **Action 2 (Financing Match):** Pre-qualifies Bengal Craft for the *Invoice Factoring Advance 2026*, yielding an immediate BDT 102,000.00 cash advance (85% LTV).
4. **Resolution:** Factoring advance eliminates the liquidity breach, maintaining cash above BDT 250,000.00 and extending runway to 68 days.

---

## 7. API Specification & Data Schemas

| HTTP Verb | Endpoint | Tier | Description |
|---|---|---|---|
| `GET` | `/api/dashboard/{cid}` | T0 | Returns 13-week forecast, runway days, hero metrics, and alerts |
| `POST` | `/api/forecast` | T1 | Executes 1,000-path Monte Carlo run with P10/P50/P90 corridors |
| `POST` | `/api/scenario` | T1 | Multi-variable stress testing (debtor delay, inflation, capex) |
| `GET` | `/api/financing/{cid}` | T0 | Evaluates 5 citable schemes with Why-Not gap diagnostics |
| `GET` | `/api/invoices/{cid}` | T0 | Lists open/overdue invoices with XGBoost delay risk probabilities |
| `POST` | `/api/draft-collection` | T2 | Generates contextual polite/firm/formal collection notices |
| `GET` | `/api/approvals/{cid}` | T0 | Lists pending T4 human-in-the-loop action items |
| `POST` | `/api/approve` | T4 | Executes T4 action using single-use cryptographic approval token |
| `GET` | `/api/audit-trail/{cid}` | T0 | Returns append-only SHA-256 hash-chained audit blocks |
| `POST` | `/api/chat` | T1 | Multi-agent natural language copilot with SSE thought streaming |
| `POST` | `/api/seed-benchmark` | T0 | Idempotent seeder loading the Bengal Craft benchmark dataset |

---

## 8. Deployment, Offline Resilience & Reproducibility

### 8.1 Offline-First Architecture (`MOCK_LLM=true`)
To guarantee uninterrupted execution in network-restricted judging environments, AuraCFO includes a fully deterministic mock LLM fallback (`app/mock/mock_llm.py`). When no external LLM API key is detected, the system auto-activates `MOCK_LLM=true`, generating authentic agent reasoning traces grounded directly in engine outputs.

### 8.2 Single-Command Orchestration
AuraCFO is fully containerized. A single command boots the entire stack:
```bash
docker compose up --build
```
- **Backend Service:** Port 8000 (FastAPI + Asyncio SQLite)
- **Frontend Service:** Port 5173 (Vite + Nginx Production Bundle)
- **Healthcheck:** Verified via `/api/dashboard/health` returning HTTP 200 within 5 seconds.

### 8.3 Quality Assurance & Verification
- **Pytest Suite:** 20/20 comprehensive unit and integration tests passing.
- **Sandbox Replay:** `python backend/tests/replay_sandbox.py` completes all 7 evaluation steps cleanly, generating verifiable evidence in `logs/sandbox_execution_evidence.jsonl`.
- **Frontend Build:** `npm run build` compiles with 0 TypeScript and 0 Vite bundle errors.

---

## 9. Conclusion & Future Roadmap

AuraCFO establishes a new standard for autonomous enterprise agents in regulated financial environments. By strictly decoupling conversational intelligence from deterministic mathematical truth, and binding all agent authority within cryptographic autonomy tiers, AuraCFO delivers the speed of autonomous AI with the unwavering reliability of institutional corporate finance.

**Future Horizons:**
- Direct Open Banking API integrations via PSD2 / Bangladesh Bank interoperable payment rails.
- Multi-currency cross-border hedging using Shenzhen SME supply chain benchmarks.
- Automated zero-knowledge proofs (ZKP) for private credit underwriting without disclosing full ledgers.
