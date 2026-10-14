# AuraCFO — Product Requirements Document (PRD)
## FinTechathon 2026 · Topic E · SME Finance Copilot

> **Version:** 1.0 · **Date:** 2026-10-14 · **Status:** LOCKED FOR BUILD
> **Owner:** AuraCFO Team
> **Competition Rubric:** Task Completion 40% · Security & Compliance 30% · Innovation & Interaction 30%

---

## 1. Product Vision

**One-line vision:**
> AuraCFO is a governed, AI-powered Virtual CFO that gives small and medium business owners real-time certainty about their cash runway, tells them exactly which financing they qualify for (and why not), and never acts on their behalf without explicit approval.

**Problem statement:**
- 59% of SMEs carry invoices overdue 30+ days but cannot predict when a cash crisis will hit
- Financing rejection is opaque — owners don't know what to fix or what documents to gather
- Existing AI tools hallucinate financial figures, creating liability rather than value
- No open product combines forecast + financing match + governed agentic actions + audit trail in one SME-facing copilot

**How AuraCFO solves it:**
- Deterministic Monte Carlo cash forecasting with probabilistic shortfall dates, not vague charts
- Financing matcher that evaluates real banking covenants and explains every rejected option
- All high-impact actions (sending emails, submitting applications) are air-gapped behind human approval
- Full SHA-256 hash-chained audit trail so every AI action is provably traceable

---

## 2. Target Users

### Persona A — The SME Owner (Primary)
| Attribute | Detail |
|---|---|
| Role | Owner/Director of a small retail, trading, or services business |
| Revenue range | USD 50,000–500,000 annually |
| Finance literacy | Moderate — understands invoices, bank balance, "cash is tight" |
| Pain points | Surprised by cash crunches; rejected by banks without explanation; chasing late payments manually |
| Tech comfort | Uses smartphone apps; comfortable with dashboards; not comfortable with spreadsheets |
| Language | English primary; Bangla secondary (stretch goal) |
| Default UI mode | **Owner Mode** — plain English, no jargon, action-oriented |

### Persona B — The Finance-Aware CFO / Accountant (Secondary)
| Attribute | Detail |
|---|---|
| Role | In-house accountant or part-time CFO for an SME |
| Finance literacy | High — understands DSCR, covenant ratios, GAAP |
| Pain points | Needs to present board-ready forecasts; wants covenant compliance visibility |
| Default UI mode | **CFO Mode** — formal terminology, DSCR formulas, p-values, covenant ratios |

### Persona C — Competition Judge (Evaluation Persona)
| Attribute | Detail |
|---|---|
| Profile | WeBank credit risk director, Tsinghua PBCSF fintech scholar |
| Evaluation focus | Does the demo work end-to-end? Are security controls real (tested) or just described? Is there a novel idea? |
| Key need | Load data in < 60 seconds, see a real forecast, see a blocked injection, see a T4 approval gate |

---

## 3. User Stories & Acceptance Criteria

### Epic 1: Cash-Flow Management

#### US-01: 13-Week Probabilistic Forecast
**As** an SME owner,
**I want** to see a 13-week cash forecast showing optimistic, median, and pessimistic scenarios,
**So that** I can plan around my worst-case cash position, not just an average.

**Acceptance Criteria:**
- [ ] AC-01.1: Dashboard displays P10 (pessimistic), P50 (median), P90 (optimistic) bands as shaded ribbons on a single chart
- [ ] AC-01.2: A horizontal safety-floor line shows the minimum operating reserve (configurable, default = 1 month burn)
- [ ] AC-01.3: The earliest date where P50 drops below the safety floor is labelled "Shortfall Date" in red
- [ ] AC-01.4: Hovering any week on the chart shows exact P10/P50/P90 values for that date
- [ ] AC-01.5: Forecast computation uses ≥1,000 Monte Carlo simulation paths
- [ ] AC-01.6: LLM is **prohibited** from performing forecast arithmetic; all values come from `forecast_engine.py`
- [ ] AC-01.7: Chart loads with shimmer skeleton while computing; never shows empty white space

#### US-02: Invoice Payment Delay Risk
**As** an SME owner,
**I want** to know which of my outstanding invoices is most likely to be paid late,
**So that** I can proactively chase the riskiest ones first.

**Acceptance Criteria:**
- [ ] AC-02.1: Each invoice shows a `P(delay)` percentage badge (e.g. "84% late risk")
- [ ] AC-02.2: Risk level classified as: Low (<30%), Medium (30–60%), High (>60%)
- [ ] AC-02.3: Delay model uses debtor history, invoice amount, days-to-due, and month
- [ ] AC-02.4: Model output is reproducible — same inputs always produce same output
- [ ] AC-02.5: If debtor has no history, model falls back to median delay heuristic and labels it "(estimated)"

#### US-03: Lead-Time-Aware Alerts
**As** an SME owner,
**I want** to receive cash alerts with enough lead time to act, not after the crisis hits,
**So that** I can arrange financing or accelerate collections before cash runs out.

**Acceptance Criteria:**
- [ ] AC-03.1: Alert system triggers when predicted shortfall is within 30 days, not just when balance is already negative
- [ ] AC-03.2: Critical alert (red): projected deficit > $0 on any P50 day within 21 days
- [ ] AC-03.3: Warning alert (amber): projected deficit > $0 on any P50 day within 30 days
- [ ] AC-03.4: Each alert includes: cause, predicted date, predicted amount, and a recommended action button
- [ ] AC-03.5: Alert copy must identify the **specific invoice** causing the shortfall if attributable

#### US-04: What-If Scenario Studio
**As** an SME owner,
**I want** to model "what if Acme Corp pays 30 days late AND my supplier costs go up 15%",
**So that** I understand compounded risk before it happens.

**Acceptance Criteria:**
- [ ] AC-04.1: Scenario Studio has 3 sliders: debtor delay (0–90 days), supplier cost shock (+0% to +30%), emergency capex ($0 to $50,000)
- [ ] AC-04.2: A toggle applies/removes a projected factoring advance to the scenario
- [ ] AC-04.3: Simulation result shows baseline vs. stressed curves on the same chart
- [ ] AC-04.4: A "Shortfall delta" badge shows how many days earlier the shortfall moves (e.g. "Shortfall accelerates by 14 days")
- [ ] AC-04.5: Preset scenarios available: Base Case, 30-Day Debtor Lag, 15% COGS Surge, Worst Case Compound
- [ ] AC-04.6: Slider changes debounce 300ms before triggering recomputation

---

### Epic 2: Financing Matcher

#### US-05: Multi-Scheme Eligibility Matching
**As** an SME owner,
**I want** to see which financing products I currently qualify for and their key terms,
**So that** I know my options without visiting 5 different banks.

**Acceptance Criteria:**
- [ ] AC-05.1: System evaluates the SME profile against ≥5 financing schemes (see scheme catalog)
- [ ] AC-05.2: Eligible schemes show: name, issuer, rate, max amount, tenure, and match score (0–100)
- [ ] AC-05.3: Ineligible schemes are shown in a separate "Not eligible" section (not hidden)
- [ ] AC-05.4: Each scheme card has a "Prepare Application" button (T3 action) and a "Why Not?" button
- [ ] AC-05.5: Scheme data carries an effective_date; schemes older than 180 days show a ⚠️ "may be stale" badge
- [ ] AC-05.6: Eligibility rules are evaluated in Python code, **not** by LLM inference

#### US-06: Covenant Health Monitor
**As** an SME owner (or accountant),
**I want** to see my exact banking covenant ratios and how far I am from each threshold,
**So that** I understand what's limiting my borrowing capacity.

**Acceptance Criteria:**
- [ ] AC-06.1: Top banner shows: DSCR, Quick Ratio, Leverage, and Burn Rate with pass/fail/warning badges
- [ ] AC-06.2: DSCR = Net Operating Income / Total Debt Service (computed from transactions, not LLM)
- [ ] AC-06.3: Quick Ratio = (Cash + Receivables) / Current Liabilities
- [ ] AC-06.4: Each ratio shows current value and the threshold required by the most relevant failed scheme
- [ ] AC-06.5: Ratios update automatically when new transaction data is ingested

#### US-07: "Why-Not" Rejection Diagnostic
**As** an SME owner,
**I want** to know exactly why I was rejected for a financing product and what to do about it,
**So that** I can fix the specific issue and become eligible.

**Acceptance Criteria:**
- [ ] AC-07.1: Clicking "Why Not?" opens a slide-over panel for that scheme
- [ ] AC-07.2: Panel lists every failed eligibility rule with: rule name, required value, your current value
- [ ] AC-07.3: Panel lists specific actionable remediation steps (e.g. "Clear $3,200 in short-term AP to elevate DSCR from 1.18 to 1.26x")
- [ ] AC-07.4: Panel lists the required documents to apply (from scheme JSON)
- [ ] AC-07.5: A "Recalculate Eligibility" button re-runs the matching engine after changes
- [ ] AC-07.6: Remediation steps are generated by the covenant engine, not improvised by LLM

#### US-08: Application Pack Compiler
**As** an SME owner,
**I want** to generate a standardized financing application pack with my verified financials,
**So that** I can approach a lender with confidence, not guesswork.

**Acceptance Criteria:**
- [ ] AC-08.1: "Prepare Application" triggers a T3 action — queues an approval request, does not submit
- [ ] AC-08.2: Pack includes: 12-month transaction summary, receivables aging, covenant ratios, DSCR trend
- [ ] AC-08.3: Pack is exportable as PDF + JSON
- [ ] AC-08.4: Pack is submitted to lender only after Tier 4 human approval from the Governance page

---

### Epic 3: Business Financial Analysis

#### US-09: Cash Conversion Cycle
**As** an accountant,
**I want** to see my business's Cash Conversion Cycle (CCC = DIO + DSO - DPO),
**So that** I can identify whether the bottleneck is inventory, receivables, or payables.

**Acceptance Criteria:**
- [ ] AC-09.1: CCC is computed and displayed on the Dashboard with a trend arrow vs. prior 30 days
- [ ] AC-09.2: DIO, DSO, and DPO are shown individually with explanations in Owner Mode
- [ ] AC-09.3: LLM provides a 1–2 sentence natural language interpretation of the CCC in context

#### US-10: Revenue Concentration Risk
**As** an SME owner,
**I want** to know if I'm too dependent on a single customer,
**So that** I can understand my exposure if they delay or default.

**Acceptance Criteria:**
- [ ] AC-10.1: System flags if any single debtor accounts for >40% of total receivables (configurable threshold)
- [ ] AC-10.2: Concentration risk displayed as a percentage bar on the Dashboard
- [ ] AC-10.3: Alert generated if top customer's share exceeds threshold

#### US-11: Dual Persona Dial
**As** a user,
**I want** to toggle between plain-English (Owner) and technical-accounting (CFO) explanations,
**So that** the tool is equally useful whether I'm a business owner or an accountant.

**Acceptance Criteria:**
- [ ] AC-11.1: A toggle control in the Copilot Drawer header switches between Owner and CFO modes
- [ ] AC-11.2: Owner mode: avoids accounting jargon, uses analogies ("Your cash is like fuel — you have 34 days left")
- [ ] AC-11.3: CFO mode: uses formal terms (DSCR, DPO, NOI), cites formula, reports p-values if available
- [ ] AC-11.4: Mode persists per browser session (localStorage)
- [ ] AC-11.5: All numerical values are identical in both modes — only narrative language changes

---

### Epic 4: Collections & Invoice Operations

#### US-12: Aged Receivables Management
**As** an SME owner,
**I want** to see my receivables grouped by aging bucket,
**So that** I can instantly spot what's overdue and by how long.

**Acceptance Criteria:**
- [ ] AC-12.1: Aging buckets: Current (not yet due), 1–30 days, 31–60 days, 60+ days overdue
- [ ] AC-12.2: Each bucket shows total amount and count of invoices
- [ ] AC-12.3: 60+ days bucket highlighted in red
- [ ] AC-12.4: Invoice table sortable by: amount, due date, delay risk, debtor name

#### US-13: Governed Collection Draft
**As** an SME owner,
**I want** to have AuraCFO draft a collection email for an overdue invoice,
**So that** I can send a professionally-worded reminder without spending time writing it.

**Acceptance Criteria:**
- [ ] AC-13.1: "Draft Reminder" action available per invoice row in the Operations table
- [ ] AC-13.2: User selects tone: Polite Nudge / Standard Firm / Formal Demand
- [ ] AC-13.3: Draft displays recipient email, subject, and full body for review before any action
- [ ] AC-13.4: Draft is **never sent automatically** — requires Tier 4 approval in Governance inbox
- [ ] AC-13.5: Draft is labelled with "Tier 2 (Draft) — Cannot send without T4 approval"
- [ ] AC-13.6: Draft does NOT contain any PII that wasn't already in the original invoice

---

### Epic 5: Security, Governance & Audit

#### US-14: Prompt Injection Firewall
**As** a system administrator,
**I want** any poisoned content in uploaded documents to be blocked,
**So that** a malicious invoice cannot hijack the AI's goals or approve unauthorized payments.

**Acceptance Criteria:**
- [ ] AC-14.1: Injection guard tests every ingested text (OCR, bank memo, invoice narrative, chat message) against ≥50 known patterns
- [ ] AC-14.2: Blocked payloads are logged with: source, pattern matched, timestamp, blocked text (truncated)
- [ ] AC-14.3: The rest of the document is processed normally after blocking the poisoned field
- [ ] AC-14.4: Blocked injection rate on test corpus ≥ 98%
- [ ] AC-14.5: OCR text is **never** concatenated directly into an LLM system prompt

#### US-15: PII Vault
**As** an SME owner,
**I want** my customers' personal data (names, tax IDs, bank accounts) to never be sent to the AI model,
**So that** I comply with data protection obligations and don't risk exposure.

**Acceptance Criteria:**
- [ ] AC-15.1: All PII is scrubbed before any payload is sent to the LLM API
- [ ] AC-15.2: PII entities detected: personal names, national IDs (BD: 13/17 digit NID), tax IDs (TIN), bank account numbers, phone numbers
- [ ] AC-15.3: Each PII entity is replaced with a deterministic HMAC token (e.g. `HMAC_CUST_8821`)
- [ ] AC-15.4: Tokens are re-hydrated back to display values only in the client-side UI layer
- [ ] AC-15.5: Governance page shows a "PII Redaction Telemetry" diff: raw input vs. sanitized context
- [ ] AC-15.6: Zero PII must appear in audit logs or LLM telemetry

#### US-16: Hash-Chained Audit Trail
**As** an SME owner and competition judge,
**I want** every AI action to be logged in a tamper-evident audit trail,
**So that** any manipulation of the history is immediately detectable.

**Acceptance Criteria:**
- [ ] AC-16.1: Every agent action logs: timestamp, agent role, tool executed, input hash, output hash, permission tier, current hash (H_n), previous hash (H_{n-1})
- [ ] AC-16.2: H_n = SHA-256(H_{n-1} || timestamp || agent_role || tool_name || payload_hash)
- [ ] AC-16.3: Governance page provides a "Verify Chain" button that checks every hash link
- [ ] AC-16.4: Any tampered entry is highlighted in red with the specific block that failed
- [ ] AC-16.5: Chain is append-only — no entry can be deleted or modified

#### US-17: Air-Gapped Human Approval (T4 Gate)
**As** an SME owner,
**I want** the AI to never send emails or submit loan applications on my behalf without my explicit confirmation,
**So that** I remain in full control of every external communication.

**Acceptance Criteria:**
- [ ] AC-17.1: Email dispatch and loan submission are Tier 4 tools — blocked at the code handler level without a valid approval token
- [ ] AC-17.2: T4 actions appear in a Governance inbox as "Pending Approval" cards
- [ ] AC-17.3: Each card shows: action type, payload summary, initiating agent, prepared artifact (draft email / loan pack)
- [ ] AC-17.4: Owner must actively click "Approve" — passive timeout does NOT auto-approve
- [ ] AC-17.5: Approved and rejected actions are both logged in the audit trail with the approval decision
- [ ] AC-17.6: LangGraph `interrupt()` is used to suspend the agent while awaiting human action

---

### Epic 6: Data Ingestion & Benchmark

#### US-18: 1-Click Benchmark Seeder
**As** a competition judge,
**I want** to load a realistic test dataset in one click,
**So that** I can evaluate the full system without preparing my own data.

**Acceptance Criteria:**
- [ ] AC-18.1: "Load Bengal Craft & Retail" button seeds 128 real anonymized transactions + 8 invoices in < 5 seconds
- [ ] AC-18.2: After seeding, the Dashboard immediately shows a live forecast with a Day 21 shortfall trigger
- [ ] AC-18.3: "Load Shenzhen Cross-Border Importer" button seeds an alternative scenario with FX/customs stress
- [ ] AC-18.4: Seeding is idempotent — clicking twice does not duplicate data
- [ ] AC-18.5: Ingestion preview shows PII redaction table before finalizing

#### US-19: CSV/PDF Ingestion
**As** an SME owner,
**I want** to upload my own bank statement (CSV or PDF) and invoice images,
**So that** I can use my real data, not synthetic test data.

**Acceptance Criteria:**
- [ ] AC-19.1: Drag-and-drop zone accepts: .csv, .xlsx, .pdf, .png, .jpg
- [ ] AC-19.2: CSV parser auto-detects columns: date, amount, description/narration, direction (credit/debit)
- [ ] AC-19.3: PDF/image invoices processed via local OCR (LayoutLMv3 or pytesseract) — no cloud OCR dependency
- [ ] AC-19.4: Ingestion preview shows detected transactions before committing to DB
- [ ] AC-19.5: PII scrubbing is applied and shown in the preview before storing

---

## 4. Non-Functional Requirements

### Performance
| Requirement | Target |
|---|---|
| Dashboard page load (with cached forecast) | < 2 seconds |
| Forecast computation (13-week, 1000 paths) | < 5 seconds |
| Scenario simulation (slider change) | < 3 seconds (debounced) |
| Copilot first thought trace appears | < 1.5 seconds |
| DB seed (128 transactions) | < 5 seconds |

### Security
| Requirement | Target |
|---|---|
| Injection block rate on 50-payload corpus | ≥ 98% |
| PII leakage to LLM | 0 instances |
| T4 actions auto-executed without approval | 0 instances |
| Audit chain tamper detection | 100% of tampered blocks detected |
| LLM arithmetic errors in output | 0 — all numbers come from engines |

### Reliability
| Requirement | Target |
|---|---|
| Works without LLM API (MOCK_LLM=true) | ✅ All math still runs live |
| Works without internet | ✅ Fully offline after Docker pull |
| Works on fresh Docker pull (clean machine) | ✅ Single `docker compose up --build` |

### Accessibility
- All semantic color pairs (solvency green, shortfall red, warning amber) must pass WCAG AA contrast on dark background
- All interactive elements must be keyboard-navigable

---

## 5. Scope

### In Scope (MVP)
- Cash-flow forecasting with P10/P50/P90 Monte Carlo
- Payment delay prediction per invoice
- Lead-time-aware alerts
- What-if scenario simulation (3 sliders)
- T0–T4 permission tier enforcement
- Financing scheme matching (5–8 schemes)
- Why-Not rejection diagnostics
- Governed collection draft (T2)
- T4 human approval gate
- SHA-256 hash-chained audit trail
- PII sanitization vault
- Prompt injection firewall (50+ payloads)
- Output number validation
- 1-click benchmark seeder (Bengal Craft)
- CSV ingestion
- Copilot drawer with SSE streaming thought traces
- MOCK_LLM offline fallback
- Docker Compose deployment
- MP4 demo video

### In Scope (Stretch — implement if Day 3 checkpoint passes early)
- Owner/CFO persona dial
- Shenzhen cross-border importer scenario
- MCP server (6 tools + 2 resources)
- GraphRAG / Neo4j scheme knowledge graph
- Bangla language copilot responses
- FX / landed-cost scenario sliders

### Out of Scope (Explicitly excluded)
- Blockchain / on-chain features (no bonus for Topic E)
- Multi-tenant user management (single-company demo)
- Real email dispatch integration (SMTP)
- Real loan submission integration (bank APIs)
- Mobile app (web responsive only)
- Recurring subscription billing
- Tax filing / accounting software replacement
- Any feature requiring cloud-only runtime (must work offline)

---

## 6. Success Metrics (Competition)

| Metric | Target |
|---|---|
| End-to-end demo completes without error | ✅ Every time |
| Sandbox replay script passes all assertions | ✅ |
| Injection corpus block rate | ≥ 98% |
| T4 auto-executed without approval | 0 |
| PII in LLM payload | 0 |
| Judge can load + see forecast in < 60s | ✅ |
| All 6 deliverables submitted before 12:00 Dhaka Oct 20 | ✅ |
