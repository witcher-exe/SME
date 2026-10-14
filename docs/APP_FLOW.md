# AuraCFO — App Flow Document
## FinTechathon 2026 · Topic E · SME Finance Copilot

> **Version:** 1.1 · **Date:** 2026-10-14 · **Status:** PATCHED & VERIFIED FOR BUILD
> **Companion to:** PRD.md (what) → TRD.md (how) → this doc (exact user journey, screen-by-screen)
> **Purpose:** Every user flow is documented as a numbered step sequence so coding agents produce the exact interaction — no guessing states, transitions, or error paths.

---

## Table of Contents

1. [Flow 1: First-Time Judge Experience (1-Click Seed → Full Demo)](#flow-1-first-time-judge-experience)
2. [Flow 2: Custom Data Ingestion (Upload CSV/PDF → PII Scrub → Preview → Commit)](#flow-2-custom-data-ingestion)
3. [Flow 3: Dashboard Exploration (Load → Read → Click Alert → Navigate)](#flow-3-dashboard-exploration)
4. [Flow 4: Forecast & Scenario Studio (View Forecast → Adjust Sliders → Compare)](#flow-4-forecast--scenario-studio)
5. [Flow 5: Financing Discovery (Browse Schemes → Why-Not → Remediation → Prepare Pack)](#flow-5-financing-discovery)
6. [Flow 6: Collection Lifecycle (View Overdue → Draft Reminder → Submit → Approve)](#flow-6-collection-lifecycle)
7. [Flow 7: Copilot Conversation (Ask Question → Thought Traces → Synthesis → Action Chips)](#flow-7-copilot-conversation)
8. [Flow 8: Governance & Audit Review (Pending Approvals → Inspect → Approve/Reject → Verify Chain)](#flow-8-governance--audit-review)
9. [Global Navigation & Persistent Elements](#global-navigation--persistent-elements)
10. [State Transition Diagrams](#state-transition-diagrams)

---

## Conventions

| Symbol | Meaning |
|---|---|
| `→` | Navigates to / triggers |
| `[Button Text]` | Clickable UI element |
| `⏳` | Loading / async state |
| `✅` | Success state |
| `❌` | Error state |
| `🔒` | Permission-gated action |
| `(T0)–(T4)` | Permission tier of the action |
| `SSE:type` | Server-Sent Event type received |

---

## Flow 1: First-Time Judge Experience

**Persona:** Competition Judge (Persona C)
**Goal:** Load realistic data, see a live forecast, explore the full system in < 60 seconds.
**Entry point:** Fresh `docker compose up --build` → browser opens `http://localhost:3000`

### Happy Path

| Step | User Action | System Response | Route | API Call |
|---|---|---|---|---|
| 1.1 | Opens `localhost:3000` in browser | App loads → **DataPage** shown (no data detected). Sidebar shows all 6 nav items but Dashboard/Forecast/Financing/Operations/Governance show a subtle lock icon indicating "no data yet" | `/data` | — |
| 1.2 | Reads the two benchmark cards: "Bengal Craft & Retail" (recommended) and "Shenzhen Cross-Border Importer" | Cards are displayed with descriptions. Bengal Craft card has a green ⚡ "Recommended" badge | `/data` | — |
| 1.3 | Clicks `[Load Bengal Craft & Retail]` | Button shows spinner + text changes to "Seeding 128 transactions..." ⏳ | `/data` | `POST /api/seed-benchmark` body: `{ scenario: "bengal_craft" }` |
| 1.4 | Waits (< 5 seconds) | Progress bar fills: "Importing transactions... Importing invoices... Computing forecast... Done ✅". PII redaction preview table appears showing 3-5 sample redactions (e.g., "Md. Karim Ullah → HMAC_CUST_9912") | `/data` | Response: `{ company_id, transactions_count: 128, invoices_count: 8, pii_entities_redacted: N }` |
| 1.5 | Sees "✅ Bengal Craft loaded" success banner | Sidebar nav items lose their lock icons. A toast notification says "Dashboard ready — shortfall detected on Day 21" | `/data` | — |
| 1.6 | Clicks `Dashboard` in sidebar | Navigates to Dashboard. All 4 hero metric cards animate in. Quantile chart renders with P10/P50/P90 ribbons. Alert feed shows a Critical alert: "Nov 04 Cash Shortfall" | `/dashboard` | `GET /api/dashboard/{company_id}` |
| 1.7 | Clicks the Critical alert → "Nov 04 Cash Shortfall" | Alert expands inline. Action button says `[View Forecast Detail]`. Clicking it navigates to Forecast page | `/dashboard` → `/forecast` | — |
| 1.8 | Explores Forecast page | Baseline P50 curve visible. Sliders at default (0/0/0). Debtor hazard table shows 8 invoices ranked by P(delay) | `/forecast` | `POST /api/forecast` |
| 1.9 | Clicks `[Ask CFO]` button in top bar | Copilot Drawer slides open from right (400px). Pre-loaded welcome message: "Bengal Craft loaded. You have 34 days of runway. Ask me anything." | Any page | — |

### Error Path — Seed Fails

| Step | Trigger | System Response |
|---|---|---|
| 1.3E | Network error or DB write failure during seed | Button stops spinner. Error banner: "Failed to seed data: {error_message}. [Retry]". Button resets to clickable state |
| 1.3E2 | User clicks `[Retry]` | Repeat step 1.3. Seeding is idempotent — partial data from failed attempt is cleaned up before retry |

### Error Path — Seed Already Exists

| Step | Trigger | System Response |
|---|---|---|
| 1.3X | User clicks `[Load Bengal Craft]` when data already exists | Confirmation modal: "Bengal Craft data already loaded. Re-seeding will replace all existing data. [Cancel] [Re-seed]" |
| 1.3X2 | User clicks `[Re-seed]` | Existing data is deleted, then fresh seed is applied. Same flow as 1.3-1.5 |

---

## Flow 2: Custom Data Ingestion

**Persona:** SME Owner (Persona A)
**Goal:** Upload own bank statement CSV and invoice images, see PII scrubbing, commit to system.
**Entry point:** `/data` page → Region B (Custom Data Intake)

### Happy Path

| Step | User Action | System Response | API Call |
|---|---|---|---|
| 2.1 | Navigates to `/data` page | DataPage loads. If data exists, Region A shows current dataset summary. Region B shows drag-and-drop zone | — |
| 2.2 | Drags a `.csv` file into the dropzone (or clicks to browse) | Dropzone border turns blue. File name and size displayed below dropzone. "Analyzing file..." spinner appears ⏳ | `POST /api/ingest` (multipart/form-data) |
| 2.3 | Waits (< 3 seconds for CSV) | **Ingestion Preview** appears (Region C): table showing detected columns (date, amount, description, direction), sample of first 10 rows, and auto-detected column mapping | Response: `{ preview: {...}, pii_entities: [...], column_mapping: {...} }` |
| 2.4 | Reviews column mapping. If auto-detection is wrong, user can reassign columns via dropdown selectors | Dropdowns for each required field: Date, Amount, Description, Direction (Credit/Debit). System validates that all 4 are mapped | — |
| 2.5 | Sees PII Redaction table: Original Entity → Sanitized HMAC Token → Category | Each detected PII entity shown with toggle "Redact ✅ / Keep ⚠️". All default to Redact | — |
| 2.6 | Clicks `[Ingest & Compute 13-Week Forecast]` | Confirmation modal: "This will import {N} transactions and redact {M} PII entities. Existing data will be replaced. [Cancel] [Confirm]" | — |
| 2.7 | Clicks `[Confirm]` | Progress: "Importing... PII scrubbing... Computing forecast... ✅ Done". Toast: "Dashboard ready" | `POST /api/ingest` (commit phase) |
| 2.8 | Clicks `Dashboard` in sidebar | Full dashboard populated with user's data | `GET /api/dashboard/{cid}` |

### PDF/Image Upload Path

| Step | User Action | System Response |
|---|---|---|
| 2.2P | Drops a `.pdf` or `.png`/`.jpg` file | Dropzone accepts. "Processing with OCR engine..." ⏳ (local LayoutLMv3/pytesseract — no cloud dependency) |
| 2.3P | Waits (< 10 seconds for PDF) | OCR extracts text → same preview table as 2.3, but with a "Source: OCR" badge. Lower confidence fields highlighted in amber with "Review" labels |
| 2.4P | User corrects any OCR misreads in the editable preview cells | Changes saved locally. "Corrected 2 fields" badge appears |
| 2.5P | Same PII review as 2.5 | Same PII redaction table |
| 2.6P–2.8P | Same as 2.6–2.8 | Same commit + navigate flow |

### Error Paths

| Step | Trigger | System Response |
|---|---|---|
| 2.2E1 | Unsupported file type (e.g., `.docx`, `.zip`) | Toast error: "Unsupported file format. Accepted: .csv, .xlsx, .pdf, .png, .jpg". Dropzone resets |
| 2.2E2 | File too large (> 10 MB) | Toast error: "File exceeds 10 MB limit. Please use a smaller export" |
| 2.3E | CSV parsing fails (no recognizable columns) | Error banner in preview area: "Could not detect transaction columns. Expected: date, amount, description. [Upload a different file]" |
| 2.3E2 | PDF OCR fails (corrupt or encrypted PDF) | Error banner: "Could not process this PDF. It may be encrypted or corrupted. [Try a different file]" |
| 2.7E | DB write failure during commit | Error banner: "Import failed: {error}. Your data was not saved. [Retry]". Preview data is preserved so user doesn't need to re-upload |

---

## Flow 3: Dashboard Exploration

**Persona:** SME Owner (Persona A) or Judge (Persona C)
**Goal:** Understand cash position at a glance, identify threats, navigate to relevant detail pages.
**Entry point:** `/dashboard` (after data is loaded)

### Happy Path

| Step | User Action | System Response | Component |
|---|---|---|---|
| 3.1 | Navigates to `/dashboard` | Page loads with shimmer skeletons (4 metric card shimmers + 1 chart shimmer + alert feed shimmer). API call fires | `DashboardPage` → `GET /api/dashboard/{cid}` |
| 3.2 | Data arrives (< 2 sec) | Shimmer → real data. Four hero metrics animate in: Runway Days (34), Current Cash ($48,200), Pending AR ($62,400), Net Monthly Burn ($14k) | `MetricCard` ×4 |
| 3.3 | Scans metrics | Each card shows: value (hero number), trend arrow (▲/▼ vs. prior 30 days), status color (green/amber/red). Runway < 30 days = red | `MetricCard` |
| 3.4 | Looks at the quantile chart | P10/P50/P90 ribbon chart renders with 13 weekly data points. Safety floor horizontal line at $10,000. Shortfall date (Nov 04) marked with red vertical line and label | `QuantileForecastChart` |
| 3.5 | Hovers over Week 6 on chart | Tooltip appears: "Week 6 (Nov 04): P10 = -$8,420 · P50 = $2,100 · P90 = $14,800. Burn rate: $3,500/wk" | `QuantileForecastChart` tooltip |
| 3.6 | Looks at Alert Feed (right column) | Two alerts visible: (1) CRITICAL "Nov 04 Cash Shortfall — $8,420 deficit (P10)" with `[View Forecast]` button. (2) WARNING "Acme Corp Delay Risk — 78% late odds" with `[Draft Reminder]` button | `AlertFeed` |
| 3.7a | Clicks `[View Forecast]` on critical alert | Navigates to `/forecast` page with baseline forecast pre-loaded | — |
| 3.7b | Clicks `[Draft Reminder]` on warning alert | Navigates to `/operations` page with the specific invoice pre-selected and collection drawer auto-opened | — |
| 3.8 | Scrolls to Region D: Active Receivables table | Table shows 8 invoices. Columns: Invoice #, Debtor, Amount, Due Date, P(Delay), Risk Rating, Action. Sorted by P(Delay) descending by default | `InvoiceTable` |
| 3.9 | Clicks an invoice row | Row expands to show detail panel: full payment history, debtor contact, last payment date. `[Draft Reminder]` button visible if overdue | `InvoiceTable` row expand |

### Empty State

| Trigger | System Response |
|---|---|
| No data loaded (fresh install) | Dashboard shows empty state: "No financial data loaded yet" with illustration. Primary CTA: `[Load Benchmark Data]` (navigates to `/data`). Secondary: `[Upload Your Own Data]` |

### Error State

| Trigger | System Response |
|---|---|
| API call fails | Metric cards show error state: red border, "Failed to load" text, `[Retry]` button per card. Chart shows error overlay. Alert feed shows "Could not load alerts" |

---

## Flow 4: Forecast & Scenario Studio

**Persona:** SME Owner (Persona A) or Accountant (Persona B)
**Goal:** Run what-if stress tests on the 13-week forecast using sliders.
**Entry point:** `/forecast` (from sidebar or from Dashboard alert click)

### Happy Path

| Step | User Action | System Response | API Call |
|---|---|---|---|
| 4.1 | Navigates to `/forecast` | Left rail (30% width): scenario controls with 4 presets + 3 sliders + 1 toggle. Right pane (70%): shimmer while forecast computes | `POST /api/forecast` body: `{ company_id }` |
| 4.2 | Forecast arrives (< 5 sec) | Right pane: solid P50 baseline curve rendered. No stressed curve yet. Below chart: debtor hazard table with 8 rows | — |
| 4.3 | Clicks preset `[30-Day Debtor Lag]` | Sliders snap: Debtor Delay → 30, Supplier Cost → 0%, Capex → $0. Debounce timer (300ms) starts | — |
| 4.4 | After 300ms debounce | ⏳ "Simulating..." overlay on chart. API fires. Results arrive (< 3 sec) | `POST /api/scenario` body: `{ company_id, debtor_delay_days: 30, supplier_cost_delta_pct: 0, capex_spend: 0, apply_factoring_advance: false }` |
| 4.5 | Scenario result renders | Dashed red line overlays the baseline. Delta badge: "Shortfall accelerates by 14 days (from Day 34 to Day 20)". Below: weekly inflow vs. outflow stacked bar | — |
| 4.6 | Manually drags Supplier Cost slider to +15% | Slider updates. 300ms debounce → API fires again with compound scenario (delay=30 + cost=+15%) | `POST /api/scenario` with updated params |
| 4.7 | Toggles `[Include Projected Factoring Advance]` | Toggle turns green. API fires with `apply_factoring_advance: true`. Chart shows third line (green dashed) = scenario + factoring | `POST /api/scenario` |
| 4.8 | Delta badge updates | "With factoring: shortfall delayed by 8 days (from Day 20 to Day 28)" | — |
| 4.9 | Clicks `[Reset to Baseline]` | All sliders reset to 0/0/0. Toggle off. Stressed curves removed. Only baseline remains | — |
| 4.10 | Scrolls to debtor hazard table | Table shows: Debtor Name, Historical Avg Delay, Invoice Amount, P(Delay), Risk Rating. Sorted by P(Delay) descending. Hover shows tooltip with debtor history | — |
| 4.11 | Clicks a high-risk debtor row | Cross-navigation: navigates to `/operations` with that debtor's invoices filtered | — |

### Preset Scenarios

| Preset | Slider Values | Purpose |
|---|---|---|
| Base Case | 0 / 0% / $0 | Baseline — no stress |
| 30-Day Debtor Lag | 30 / 0% / $0 | What if top debtor pays 30 days late? |
| 15% COGS Surge | 0 / 15% / $0 | What if supplier costs spike? |
| Worst Case Compound | 30 / 15% / $5,000 | All stresses combined |

### Error Paths

| Step | Trigger | System Response |
|---|---|---|
| 4.4E | Scenario computation fails | Chart shows error overlay: "Simulation failed. [Retry]". Sliders remain at current positions for retry |
| 4.1E | No data loaded | Empty state: "Load financial data first to run forecasts. [Go to Data Page]" |

---

## Flow 5: Financing Discovery

**Persona:** SME Owner (Persona A)
**Goal:** See which financing products I qualify for, understand why I don't qualify for others, prepare an application.
**Entry point:** `/financing`

### Happy Path

| Step | User Action | System Response | API Call |
|---|---|---|---|
| 5.1 | Navigates to `/financing` | Page loads with shimmer. Covenant health banner shimmers at top | `GET /api/financing/{company_id}` |
| 5.2 | Data arrives | **Region A (Covenant Banner):** 4 gauge cards — DSCR: 1.18x (Req: 1.25x) ⚠️, Quick Ratio: 1.45x ✅, Leverage: 2.1x ✅, Burn: $8.4k/mo. Each gauge shows current value, required threshold, and pass/fail/warning badge | `CovenantGauge` ×4 |
| 5.3 | Scans Region B: Eligible Schemes | Grid of `SchemeCard` components for eligible schemes. Each shows: name, issuer, rate, max amount, tenure, match score (0–100). Green border. `[Prepare Application (T3)]` button. If scheme data > 180 days old: ⚠️ "may be stale" badge | `SchemeCard` |
| 5.4 | Scans Region C: Ineligible Schemes | Grid of ineligible schemes. Red/amber border. Each shows: name, issuer, "INELIGIBLE" status, primary failure reason. `[Why Not?]` button | `SchemeCard` (ineligible variant) |
| 5.5 | Clicks `[Why Not?]` on "Commercial Bank Term Facility" | **Why-Not Drawer** slides in from right (overlays Copilot Drawer if open). Shows: (a) Header: "Why was Commercial Bank Term Facility rejected?" (b) Failed rules table: Rule Name → Required → Your Value → Status. (c) Remediation steps: "Step 1: Pay down $3,200 in short-term AP to elevate DSCR from 1.18x to 1.26x" (d) Required documents list. (e) `[Recalculate Eligibility]` button | — |
| 5.6 | Reads remediation steps | Steps are numbered, actionable, and generated by the covenant engine (not LLM). Each step shows the exact number change expected | — |
| 5.7 | Clicks `[Recalculate Eligibility]` | Drawer shows spinner. Re-runs matching engine. If nothing changed: "No eligibility changes detected." If improved: scheme card moves to eligible section with animation | `GET /api/financing/{cid}` (re-fetch) |
| 5.8 | Clicks `[Prepare Application (T3)]` on an eligible scheme | 🔒 T3 action. Sends `"Prepare financing application for scheme {scheme_id}"` to `/api/chat`. Treasurer agent compiles pack and queues a `financing_pack` approval request in the Governance inbox. Toast: "Application pack prepared and sent to Governance inbox." | `POST /api/chat` (SSE emits `approval_required`) |
| 5.9 | Navigates to `/governance` | Sees the pending T4 approval for the application pack | — |

### Error Paths

| Step | Trigger | System Response |
|---|---|---|
| 5.1E | No data loaded | Empty state: "Upload financial data to see financing matches. [Go to Data Page]" |
| 5.2E | Covenant computation fails | Banner shows error: "Could not compute covenant ratios. [Retry]" |

---

## Flow 6: Collection Lifecycle

**Persona:** SME Owner (Persona A)
**Goal:** Identify overdue invoices, draft a collection reminder email, submit it for approval, then approve/reject.
**Entry point:** `/operations`

### Happy Path

| Step | User Action | System Response | API Call |
|---|---|---|---|
| 6.1 | Navigates to `/operations` | Page loads. Region A: Aged Receivables Pipeline (4 buckets). Region B: Invoice Ledger Table | `GET /api/invoices/{company_id}` |
| 6.2 | Reads aging pipeline | Four bucket cards: Current ($44,300), 1-30 Days ($12,400), 31-60 Days ($5,200), 60+ Days ($2,800 ⚠️ red highlight). Each shows count of invoices | — |
| 6.3 | Clicks the "60+ Days" bucket card | Invoice table filters to show only 60+ days overdue invoices | — |
| 6.4 | Reviews invoice table | Columns: Select (checkbox), Invoice #, Debtor, Amount, Issued, Due Date, Status, Delay Risk (P%), Action. Sortable by any column. Current sort: Delay Risk descending | — |
| 6.5 | Clicks `[Draft Reminder]` on Invoice #INV-1082 (Bashundhara Paper, $6,400, 84% delay risk) | **Collection Drawer** opens (Region C). Shows: (a) Recipient: `accounts@bashundharapaper.com` (b) Tone selector: `[Polite Nudge]` `[Standard Firm]` `[Formal Demand]` — default: Standard Firm (c) "Generating draft..." ⏳ | `POST /api/draft-collection` body: `{ invoice_id, tone: "standard_firm" }` |
| 6.6 | Draft arrives (< 3 sec) | Full email draft displayed: Subject line + body text. Governance guardrail banner: "⚠️ This is a Tier 2 Draft. Email cannot be sent without Tier 4 human approval." Button: `[Submit to Owner Approval Inbox (T4)]` | — |
| 6.7 | Changes tone to `[Polite Nudge]` | Draft regenerates with softer language. API fires again with `tone: "polite_nudge"` | `POST /api/draft-collection` |
| 6.8 | Reviews the draft, satisfied | Draft shows: sender, recipient, subject, body. No PII that wasn't already in the original invoice | — |
| 6.9 | Clicks `[Submit to Owner Approval Inbox (T4)]` | 🔒 T2→T4 handoff. Confirms queuing the draft (`queue_for_approval: true` on `/api/draft-collection`, which creates the `pending` Approval record and returns `approval_id`). Toast: "Collection reminder submitted for approval. Go to Governance page to approve." Drawer shows "Pending Approval" status badge (amber) | `POST /api/draft-collection` (returns `approval_id`) |
| 6.10 | Navigates to `/governance` (or clicks toast link) | Sees new pending approval card for the collection email. Picks up at Flow 8 | — |

### Batch Draft Flow

| Step | User Action | System Response |
|---|---|---|
| 6.5B | Selects multiple invoices via checkboxes, clicks `[Draft Reminders for Selected]` | Collection drawer opens with "Batch mode: 3 invoices selected". One combined draft or 3 individual drafts (tab switcher). Same approval flow per draft |

### Error Paths

| Step | Trigger | System Response |
|---|---|---|
| 6.5E | Draft generation fails (LLM offline, MOCK_LLM=true returns cached draft) | If MOCK_LLM: cached draft is used with badge "Generated from cached template". If total failure: error in drawer "Could not generate draft. [Retry]" |
| 6.1E | No data loaded | Empty state: "No invoices found. Load data first. [Go to Data Page]" |

---

## Flow 7: Copilot Conversation

**Persona:** Any user
**Goal:** Ask AuraCFO a natural-language question and get an AI-synthesized answer backed by deterministic engine results.
**Entry point:** Click `[Ask CFO]` in Topbar (any page) or type in drawer input

### Happy Path

| Step | User Action | System Response | SSE Events |
|---|---|---|---|
| 7.1 | Clicks `[Ask CFO]` button in Topbar | Copilot Drawer slides open from right edge (400px wide, z-50). If already open, focuses the input field | — |
| 7.2 | Types: "When will I run out of cash if Acme Corp pays 30 days late?" | Message appears in drawer as user bubble (right-aligned, dark surface) | — |
| 7.3 | Presses Enter or clicks `[Send ➤]` | Input field clears. "Thinking..." shimmer appears below user message | `POST /api/chat` (SSE stream opens) |
| 7.4 | First SSE event arrives (< 1.5 sec) | **Thought Stream** starts: collapsible thought bubbles appear with agent-indigo left border | `SSE:thought` → `{ agent: "risk_sentinel", text: "Checking input for injection patterns... Clean ✅" }` |
| 7.5 | More thoughts stream in | Thought 2: `{ agent: "orchestrator", text: "Routing to Quant Modeler for scenario analysis..." }`. Thought 3: `{ agent: "quant_modeler", text: "Running Monte Carlo with debtor_delay=30..." }` | `SSE:thought` ×N |
| 7.6 | Tool call events appear | Collapsible tool-call cards: "🔧 forecast_cash() → 13 weeks computed". "🔧 simulate_scenario() → shortfall at Day 20" | `SSE:tool_call` → `SSE:tool_result` |
| 7.7 | Synthesis arrives | **Executive Synthesis** (main answer) renders in a distinct card with white text on surface background. Content: "If Acme Corp pays 30 days late, your cash shortfall accelerates from Day 34 to Day 20 — November 4th becomes October 21st. The deficit would be $12,400 instead of $8,420. I recommend: (1) Draw $10,000 invoice factoring advance, (2) Issue a formal payment reminder." | `SSE:synthesis` → `{ text: "...", citations: ["forecast_engine", "scenario_engine"] }` |
| 7.8 | Action chips appear below synthesis | Three quick-action buttons: `[Prepare Factoring Draw]` `[Draft Acme Reminder]` `[Run Another Stress Test]` | — |
| 7.9 | Clicks `[Draft Acme Reminder]` | New message sent to chat: "Draft a collection reminder for Acme Corp Invoice #1042". Triggers Flow 6 steps 6.5–6.9 inline in the drawer (drawer shows the draft preview without navigating) | `POST /api/chat` (new SSE stream) |
| 7.10 | Done event | Stream closes. Input re-enabled for next question | `SSE:done` |

### Persona Toggle

| Step | User Action | System Response |
|---|---|---|
| 7.T1 | Clicks persona toggle in Drawer header: switches from "Owner" to "CFO" | Toggle slides. All subsequent responses use formal terminology: DSCR, DPO, NOI, p-values instead of plain English analogies. Numbers remain identical |
| 7.T2 | Asks same question in CFO mode | Response: "Under a 30-day AR extension scenario, P50 shortfall date shifts from t=34 to t=20. Projected deficit: $12,400 (P10). DSCR drops from 1.18x to 0.94x. Recommended actions: invoice factoring (cost basis: 2.5% fee on $16,200 advance) or formal demand notice." |

### T4 Approval Trigger via Chat

| Step | User Action | System Response | SSE Event |
|---|---|---|---|
| 7.A1 | Types: "Send a payment reminder email to Acme Corp" | Chat processes request | `SSE:thought` stream |
| 7.A2 | System detects T4 action (email dispatch) | Thought: "This requires Tier 4 human approval. Creating approval request..." | `SSE:approval_required` → `{ approval_id: "...", action_type: "email_dispatch" }` |
| 7.A3 | Approval card appears inline in chat | Card shows: "🔒 Action requires approval: Send email to Acme Corp. [Go to Governance Page]". Email is NOT sent. LangGraph `interrupt()` pauses the graph | — |

### Error Paths

| Step | Trigger | System Response | SSE Event |
|---|---|---|---|
| 7.E1 | Injection detected in user input | Drawer shows: "⚠️ Input blocked: potentially unsafe content detected. Please rephrase your question." Red border on blocked message | `SSE:error` → `{ code: "INJECTION_BLOCKED", message: "..." }` |
| 7.E2 | LLM API fails mid-stream | Thought stream shows: "❌ Model unavailable. Switching to cached response..." If MOCK_LLM can serve: cached synthesis. If not: "Could not generate a response. All engine computations completed — view results on Dashboard." | `SSE:error` |
| 7.E3 | Output validator detects hallucinated number | Post-flight catches it. Synthesis is rewritten without the hallucinated figure, or a disclaimer badge: "⚠️ One figure could not be verified against engine output and was removed" | Corrected `SSE:synthesis` |

---

## Flow 8: Governance & Audit Review

**Persona:** SME Owner (Persona A) — the approver
**Goal:** Review pending agent actions, approve or reject, verify the audit trail integrity.
**Entry point:** `/governance`

### Happy Path

| Step | User Action | System Response | API Call |
|---|---|---|---|
| 8.1 | Navigates to `/governance` | Page loads with 3 regions: (A) Pending Approvals, (B) Audit Trail, (C) PII Redaction Telemetry | `GET /api/approvals/{cid}`, `GET /api/audit-trail/{cid}` |
| 8.2 | Sees Region A: Pending Approval Inbox | Cards for each pending T4 action. Example: "Submit Financing Application to WeBank — Initiator: Virtual CFO Agent — Amount: $20,000 — Prepared Package Hash: #7a91" | `ApprovalCard` |
| 8.3 | Clicks `[Review Details]` on an approval card | Card expands to show full payload: (a) Draft email content (for collection) or application pack summary (for financing). (b) Initiating agent role. (c) Timestamp. (d) Hash of the prepared artifact | — |
| 8.4a | Clicks `[Approve]` | Confirmation modal: "You are approving: Send collection email to Bashundhara Paper (Invoice #INV-1082, $6,400). This action is irreversible. [Cancel] [Confirm Approval]" | — |
| 8.5a | Clicks `[Confirm Approval]` | 🔒 Approval recorded. Card status changes: "Pending" → "Approved ✅". Audit entry logged. In production, this would trigger the actual email/submission. In demo: toast "Action approved and logged. (Email dispatch simulated in demo mode)" | `POST /api/approve` body: `{ approval_id, decision: "approved" }` |
| 8.4b | Clicks `[Reject]` instead | Rejection modal: "Reason for rejection (optional): [text input]. [Cancel] [Confirm Rejection]" | — |
| 8.5b | Enters reason, clicks `[Confirm Rejection]` | Card status: "Pending" → "Rejected ❌ — Reason: {text}". Audit entry logged. The suspended LangGraph is resumed with rejection, and the agent is notified | `POST /api/approve` body: `{ approval_id, decision: "rejected", reason: "..." }` |
| 8.6 | Scrolls to Region B: Audit Trail | Table shows the full hash chain: Block #, Timestamp, Agent Role, Tool Executed, Input Hash, Output Hash, H_n, H_{n-1}, Status (Verified ✅ or Tampered ❌) | `AuditTrailTable` |
| 8.7 | Clicks `[Verify Chain Integrity]` button | System fetches full audit trail and recomputes every SHA-256 link client-side alongside server's `chain_intact` flag. Progress bar: "Verifying block 1/104... 104/104". Result: "✅ All 104 blocks verified. Chain integrity confirmed." or "❌ Block 47 failed verification — hash mismatch" | `GET /api/audit-trail/{cid}` + client-side SHA-256 verification |
| 8.8 | Scrolls to Region C: PII Redaction Telemetry | Interactive diff view: Left column "Raw Input" → Right column "Sanitized (sent to LLM)". PII entities highlighted in red (raw) and green (HMAC token). Metric: "100% of PII scrubbed. 0 leaks." | `PIIRedactionDiff` |

### Audit Trail Pagination

| Step | User Action | System Response |
|---|---|---|
| 8.6P | Scrolls to bottom of audit table | "Load more" button or infinite scroll. Next page loads 50 more entries | `GET /api/audit-trail/{cid}?offset=50&limit=50` |

### Error Paths

| Step | Trigger | System Response |
|---|---|---|
| 8.5E | Approval API fails | Modal shows error: "Could not record approval. [Retry]". Card remains in "Pending" state |
| 8.7E | Chain verification finds tampered block | Table row for tampered block: red background, "❌ TAMPERED" badge. Alert banner at top: "⚠️ Audit chain integrity violation detected at block {N}. Previous hash mismatch." |

---

## Flow 9: Cross-Page Navigation & Deep Links

### Global Navigation (Sidebar)

| Nav Item | Route | Icon | Badge |
|---|---|---|---|
| Dashboard | `/dashboard` | `LayoutDashboard` | Red dot if critical alert exists |
| Forecast | `/forecast` | `TrendingUp` | — |
| Financing | `/financing` | `Landmark` | Count of eligible schemes |
| Operations | `/operations` | `FileText` | Count of overdue invoices |
| Governance | `/governance` | `Shield` | Count of pending approvals |
| Data | `/data` | `Database` | — |

### Alert-Driven Navigation

| Alert Action | Source Page | Target Page | Behavior |
|---|---|---|---|
| "View Forecast Detail" | `/dashboard` | `/forecast` | Pre-loads baseline forecast |
| "Draft Reminder" | `/dashboard` | `/operations` | Auto-opens collection drawer for the specific invoice |
| "Open Financing" | `/dashboard` | `/financing` | Scrolls to the relevant scheme card |
| "Go to Governance" | Any (Copilot Drawer) | `/governance` | Highlights the specific pending approval |

### Persistent Copilot Drawer

| Behavior | Detail |
|---|---|
| Persistence | Drawer state persists across page navigation (rendered in `App.tsx`, not per-page) |
| Open/Close | Toggle via `[Ask CFO]` button in Topbar or keyboard shortcut (Cmd/Ctrl + K) |
| Width | Fixed 400px. Page content adjusts (margin-right) when drawer is open |
| Z-index | z-50 — above page content, below modals (z-[100]) |
| Mobile | Drawer becomes full-screen overlay on viewports < 768px |

---

## State Transition Diagrams

### Approval Lifecycle

```
                    ┌──────────────┐
                    │   CREATED    │  (Agent initiates T3/T4 action)
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
         ┌─────────│   PENDING    │──────────┐
         │         └──────────────┘          │
         │ [Approve]                [Reject] │
         ▼                                   ▼
  ┌──────────────┐                   ┌──────────────┐
  │   APPROVED   │                   │   REJECTED   │
  │  (Immutable) │                   │  (Immutable) │
  └──────────────┘                   └──────────────┘
         │                                   │
         ▼                                   ▼
  Action executed                   Agent notified;
  (email sent /                     graph resumes with
   app submitted)                   rejection response
```

### Invoice Status Lifecycle

```
  ┌──────────┐     Due date      ┌───────────┐     Payment      ┌──────────┐
  │  ISSUED  │ ──── passes ────→ │  OVERDUE  │ ──── received ──→│   PAID   │
  └──────────┘                   └───────────┘                   └──────────┘
       │                              │
       │ Payment received             │ Write-off
       │ before due date              │
       ▼                              ▼
  ┌──────────┐                   ┌───────────┐
  │   PAID   │                   │WRITTEN_OFF│
  └──────────┘                   └───────────┘
```

### Data Ingestion State Machine

```
  ┌──────────┐    File      ┌───────────┐    Parsed     ┌──────────────┐
  │   IDLE   │ ── drop ──→ │ UPLOADING │ ── OK ──────→ │  PREVIEWING  │
  └──────────┘              └───────────┘                └──────┬───────┘
                                 │                              │
                            Parse fails                    [Confirm]
                                 │                              │
                                 ▼                              ▼
                            ┌─────────┐                  ┌──────────────┐
                            │  ERROR  │                  │  COMMITTING  │
                            │ [Retry] │                  └──────┬───────┘
                            └─────────┘                         │
                                                           Commit OK
                                                                │
                                                                ▼
                                                         ┌──────────────┐
                                                         │   COMPLETE   │
                                                         │  ✅ Done      │
                                                         └──────────────┘
```

### Copilot Chat Message Lifecycle

```
  User sends message
        │
        ▼
  ┌──────────────┐
  │   SENDING    │  (Input disabled, shimmer shown)
  └──────┬───────┘
         │ SSE stream opens
         ▼
  ┌──────────────┐
  │  STREAMING   │  (Thoughts + tool calls arrive progressively)
  └──────┬───────┘
         │
    ┌────┴──────┐
    │           │
    ▼           ▼
  SSE:done    SSE:approval_required
    │           │
    ▼           ▼
  ┌──────┐   ┌───────────────┐
  │ DONE │   │ AWAITING_HITL │  (Graph paused, approval card shown)
  └──────┘   └───────────────┘
```

---

## Quick Reference: Flow → Route → API → Component Mapping

| Flow | Primary Route | Key API Endpoints | Key Components |
|---|---|---|---|
| F1: Judge Seed | `/data` | `POST /api/seed-benchmark` | `BenchmarkSeeder`, `IngestionPreview` |
| F2: Data Ingest | `/data` | `POST /api/ingest` | `FileDropzone`, `IngestionPreview` |
| F3: Dashboard | `/dashboard` | `GET /api/dashboard/{cid}` | `MetricCard`, `QuantileForecastChart`, `AlertFeed`, `InvoiceTable` |
| F4: Forecast | `/forecast` | `POST /api/forecast`, `POST /api/scenario` | `ScenarioComparisonChart`, `CashFlowBarChart` |
| F5: Financing | `/financing` | `GET /api/financing/{cid}` | `CovenantGauge`, `SchemeCard`, `WhyNotDrawer` |
| F6: Collections | `/operations` | `GET /api/invoices/{cid}`, `POST /api/draft-collection` | `InvoiceTable`, Collection Drawer |
| F7: Copilot | Global Drawer | `POST /api/chat` (SSE) | `CopilotDrawer`, `ThoughtStream`, `ActionChips` |
| F8: Governance | `/governance` | `GET /api/approvals/{cid}`, `GET /api/audit-trail/{cid}`, `POST /api/approve` | `ApprovalCard`, `AuditTrailTable`, `PIIRedactionDiff` |
