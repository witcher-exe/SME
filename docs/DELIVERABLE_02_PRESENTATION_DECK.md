# AuraCFO — Deliverable 02: Presentation Slide Deck Outline
**Project:** AuraCFO — Autonomous Virtual CFO for SMEs  
**Hackathon:** FinTechathon 2026 (Topic E: Autonomous Financial Agents)  
**Format:** 14 Slides (Executive Pitch & Technical Architecture Deck)  
**Rubric Mapping:** 40% Task Completion / 30% Security & Compliance / 30% Innovation & Interaction

---

### Slide 1: Title & Overview
- **Header:** AuraCFO: The Autonomous Virtual CFO for SMEs
- **Subheader:** Predictive Treasury Management, Real-Time Covenant Compliance & Cryptographic Governance
- **Badge:** FinTechathon 2026 — Topic E: Autonomous Financial Agents
- **Presenter Team:** AuraCFO Engineering Team
- **Core Value Proposition:** Empowering the 90% of SMEs without dedicated CFOs with proactive 13-week runway forecasting, automated working capital interventions, and bank-grade credit underwriting readiness.

---

### Slide 2: The SME Working Capital Crisis (Problem Statement)
- **The Reality:** 82% of SME failures stem from poor cash-flow visibility, not lack of profitability.
- **The Pain Points:**
  - **The Blind Spot:** Invoices are delivered on Net-30/60 terms, but cash shortfalls arrive unannounced.
  - **The Covenant Trap:** Small businesses violate debt service covenants (e.g., DSCR < 1.25x) without realizing it, locking them out of institutional refinancing.
  - **The Financing Black Box:** SMEs apply to misaligned credit schemes, get rejected, and receive zero actionable feedback on how to fix their balance sheet.
- **Why Generic LLMs Fail:** Standard generative AI hallucinates numbers, cannot perform deterministic Monte Carlo simulations, leaks PII to external APIs, and acts without permission.

---

### Slide 3: AuraCFO Solution: The Hybrid Architectural Model
- **Core Philosophy:** *Zero-Hallucination Math + Cryptographically Gated Autonomy.*
- **Three Pillar System:**
  1. **Deterministic Compute Core:** Pure Python financial math (Monte Carlo, XGBoost delay risk, covenant equations). Zero LLM imports.
  2. **Multi-Agent Orchestrator:** LangGraph state machine coordinating specialized agents (Quant, Treasurer, Risk Sentinel).
  3. **Security & Governance Vault:** HMAC-SHA-256 PII tokenization, T0–T4 autonomy tiers, and SHA-256 Merkle-style audit chaining.

---

### Slide 4: System Architecture Blueprint
- **Diagram Flow:**
  - Ingestion (CSV / Open Banking) $\rightarrow$ PII Sanitizer $\rightarrow$ Isolated SQLite Ledger
  - Compute Engines (Monte Carlo, Covenant, Scheme Matcher) $\rightarrow$ Deterministic State
  - Multi-Agent Orchestrator (LangGraph: Orchestrator $\leftrightarrow$ Quant $\leftrightarrow$ Treasurer $\leftrightarrow$ Risk Sentinel)
  - Output Validator + Injection Guard $\rightarrow$ Frontend UI Shell (React 19 + Tailwind CSS)
  - Cryptographic Audit Logger $\rightarrow$ Immutable Hash Chain
- **Key Metric:** Total decoupling between computational truth and conversational reasoning.

---

### Slide 5: Deterministic Financial Engines (Zero LLM Math)
- **Engine Breakdown:**
  - **Monte Carlo 1,000-Run Simulation (`forecast_engine.py`):** Computes P10 (conservative), P50 (median), and P90 (optimistic) cash corridors over 13 weeks.
  - **XGBoost Debtor Delay Risk Scoring:** Evaluates historical DSO, dispute flags, and payment lag to forecast receivable timing adjustments.
  - **Covenant Verification Engine (`covenant_engine.py`):**
    - $\text{DSCR} = \frac{\text{Net Operating Income}}{\text{Total Debt Service}}$ (Benchmark: 1.18x vs 1.25x hurdle)
    - $\text{Quick Ratio} = \frac{\text{Cash} + \text{Marketable Securities} + \text{Receivables}}{\text{Current Liabilities}}$ (3.94x)
    - $\text{Leverage Ratio} = \frac{\text{Total Debt}}{\text{EBITDA}}$ (1.61x)
  - **WeBank Underwriting Readiness Score (0–100):** Comprehensive creditworthiness index.

---

### Slide 6: Financing Matcher & "Why-Not" X-Ray Diagnostics
- **5 Citable Regulatory Schemes Evaluated:**
  - 1. CMSME Working Capital Scheme 2026 (Ineligible — DSCR 1.18x < 1.25x)
  - 2. Invoice Factoring Advance 2026 (Eligible — Quick Ratio 3.94x > 1.20x)
  - 3. Digital Nano-Credit Micro Facility 2026 (Eligible — Fast working capital bridge)
  - 4. Women Entrepreneur Refinance Fund (Ineligible — Ownership requirement)
  - 5. Agro-Processing Export Facility (Ineligible — Sector mismatch)
- **Winning Innovation: "Why-Not" Diagnostics:**
  - For every rejected scheme, AuraCFO generates a mathematical gap analysis, actionable remediation steps (e.g., *"Pay down BDT 3,200 in AP to lift DSCR to 1.26x"*), and an exact documentary checklist.

---

### Slide 7: Security: T0–T4 Autonomy Tiers & Cryptographic Gates
- **Autonomy Boundaries:**
  - **Tier 0 (Observe):** Read-only data ingestion and dashboard rendering (Autonomous).
  - **Tier 1 (Analyze):** Running Monte Carlo simulations and scenario stress tests (Autonomous).
  - **Tier 2 (Draft):** Generating polite, firm, or formal collection notices (Autonomous Draft, Passive Owner Notification).
  - **Tier 3 (Advise):** Recommending debt restructuring or factoring facilities (Owner Acknowledgement required).
  - **Tier 4 (Execute):** Sending legal collection demands, dispatching factoring applications, or committing funds (Cryptographic HITL Approval Gate).
- **Physical Enforcement:** Backend routes strictly reject T4 execution without a cryptographically verified, single-use `ApprovalToken`.

---

### Slide 8: Data Privacy: Zero-Knowledge PII Tokenization
- **Pre-LLM Sanitization Pipeline:**
  - Raw bank narration: `"Cheque deposit from Rahim Textile Ltd TIN-94827104"`
  - PII Sanitizer replaces entities with salted HMAC tokens: `"Cheque deposit from VEND-8f4b TAXP-3a9c"`
  - Salt is stored locally in SME environment (`HMAC_SECRET_KEY`).
  - LLM only ever operates on anonymized tokens.
- **Judge-Facing Transparency:** The Governance page provides a real-time PII Redaction Diff Table showing exact original-to-token mappings.

---

### Slide 9: Auditability: SHA-256 Hash Chaining & Tamper Simulator
- **Immutable Ledger:**
  $$H_n = \text{SHA-256}(H_{n-1} \,\|\, \text{Timestamp} \,\|\, \text{Tier} \,\|\, \text{Action} \,\|\, \text{Actor} \,\|\, \text{SHA-256}(\text{Details}))$$
- **Judge-Facing Tamper Simulator (`TamperSimulatorBar.tsx`):**
  - Live interactive tool in the Governance tab allowing judges to inject a synthetic database modification.
  - The client-side and server-side verification immediately flags the broken block in red, proving audit immutability live during evaluation.

---

### Slide 10: Benchmark Demonstration: Bengal Craft & Retail
- **Real-World SME Scenario:**
  - Industry: Handicrafts & Textile Retail (Dhaka, Bangladesh)
  - Historical Data: 128 ledger transactions, 56 invoices, initial cash BDT 450,000.
- **The Working Capital Cliff:**
  - On Day 21 (November 4, 2026), two anchor debtors delay payment by 14 days while raw silk supplier invoice (BDT 180,000) falls due.
  - Cash dips to **-BDT 42,300** (breaching the BDT 220,000 safety floor).
- **AuraCFO Proactive Intervention:**
  - Day 1: System sounds Level 2 alert (14-day advance notice).
  - Proposes two parallel remediations: (A) Factoring BDT 120,000 invoice with WeBank partner, (B) Dispatching firm reminder to Apex Retailers.

---

### Slide 11: Real-Time What-If Stress Testing
- **Interactive Simulation Controls:**
  - Debtor Delay Slider (+0 to +30 days)
  - Supplier Cost Inflation (+0% to +25%)
  - Capex Outlay Simulation (Emergency equipment replacement)
  - Factoring Bridge Activation Toggle
- **Instant Visual Delta:** Monte Carlo forecast recalculates in <200ms, displaying the exact delta days until cash exhaustion and comparing baseline vs stressed trajectories.

---

### Slide 12: Natural Language Copilot with Live Thought Stream
- **Interactive Financial Assistant:**
  - Floating 400px Copilot Drawer accessible from every screen.
  - Server-Sent Events (SSE) streaming thought traces:
    - *Thinking: Checking DSCR covenant thresholds...*
    - *Action: Querying invoice factoring eligibility...*
    - *Synthesizing: Preparing executive summary for owner...*
  - Suggested prompt pills: *"Why did CMSME scheme reject me?"*, *"Simulate a 15-day debtor delay"*, *"Draft an urgent collection notice"*.

---

### Slide 13: Technical Architecture & Offline Resilience
- **Tech Stack:**
  - **Backend:** FastAPI, Python 3.12, SQLAlchemy 2.0 (Asyncio), SQLite, NumPy, SciPy, Pydantic v2.
  - **Agent Framework:** LangGraph state machine with memory checkpointers.
  - **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, Recharts, Lucide Icons (Zero React 18 peer-dependency conflicts).
  - **Offline-First Resilience:** `MOCK_LLM=true` generates deterministic synthetic agent traces without requiring external internet or API keys.
  - **Packaging:** Single-command `docker compose up --build` and unified `Makefile`.

---

### Slide 14: Conclusion & Competitive Advantage
- **Evaluation Criteria Alignment:**
  - **Task Completion (40%):** Complete working capital lifecycle (forecast, covenants, matching, collection drafts, approvals).
  - **Security & Compliance (30%):** T0–T4 permission enforcement, pre-LLM PII scrubbing, SHA-256 tamper-evident ledger, 50+ injection defenses.
  - **Innovation & Interaction (30%):** Why-Not X-Ray diagnostics, live Tamper Simulator, SSE thought streaming, real-world SME benchmark.
- **Vision:** Turning every small business into an institutionally bankable enterprise.
