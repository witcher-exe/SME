# AuraCFO — Deliverable 03: Demo Video Script & Walkthrough Guide
**Project:** AuraCFO — Autonomous Virtual CFO for SMEs  
**Hackathon:** FinTechathon 2026 (Topic E: Autonomous Financial Agents)  
**Target Duration:** 4 Minutes 30 Seconds (270 seconds)  
**Video Resolution:** 1080p 60fps  
**Audio Track:** Clear Voiceover + Subtitles  
**Format:** Timestamped Scene-by-Scene Script with Visual Directives & Audio Narration

---

### [00:00 – 00:30] Phase 1: Introduction & The SME Cash-Flow Dilemma
- **Visual:** 
  - Terminal window opens. User runs `make dev` or `docker compose up`. Fast startup logs stream past: *FastAPI backend online at :8000, Vite frontend online at :5173*.
  - Browser transitions to `http://localhost:5173`.
  - AuraCFO title card appears: *"AuraCFO: Autonomous Virtual CFO for SMEs — Zero Hallucination Math & Cryptographically Gated Autonomy."*
- **Voiceover Narration:**
  > "Welcome to AuraCFO. 82% of small and medium businesses don't fail because they lack sales—they fail because working capital dries up in the gap between billing an invoice and collecting the cash. Today, we demonstrate how AuraCFO acts as an always-on, autonomous virtual CFO for Bengal Craft & Retail, a boutique textile manufacturer in Dhaka facing a sudden liquidity cliff."

---

### [00:30 – 01:15] Phase 2: Dashboard Overview & The Day 21 Liquidity Radar
- **Visual:**
  - Browser opens to `/dashboard`.
  - Hero metric cards highlight:
    - **Current Liquid Cash:** BDT 450,000.
    - **Runway:** 21 Days (Red Alert badge).
    - **Safety Floor Breach:** November 4, 2026 (-BDT 42,300).
    - **WeBank Underwriting Readiness Score:** 72/100.
  - Camera zooms into the 13-Week Monte Carlo cash-flow corridor (Recharts P10/P50/P90 bands).
  - Hovering on Week 3 reveals the exact dip below the BDT 220,000 minimum operating buffer.
  - Below the chart, the Overdue Receivables table lists 6 invoices with XGBoost delay risk scores ($P(\text{delay}) > 0.65$).
- **Voiceover Narration:**
  > "Upon loading the Bengal Craft benchmark, AuraCFO's deterministic Monte Carlo engine immediately projects cash balances across 1,000 simulated paths over the next 13 weeks. Notice the red alert: without intervention, Bengal Craft will breach its safety reserve on November 4th—exactly 21 days from today. Two primary debtors, Apex Retailers and Dhaka Department Stores, are flagged by our logistic delay scoring model with an 85% probability of a 14-day delay."

---

### [01:15 – 02:00] Phase 3: What-If Stress Testing & Scenario Engine
- **Visual:**
  - User clicks on `/forecast` tab.
  - Interactive sliders:
    - User drags **Debtor Delay Slider** from +0 to +14 days.
    - User adjusts **Supplier Inflation Slider** to +10%.
  - The chart updates dynamically in real-time (<150ms).
  - The "Delta Days to Shortfall" indicator shifts from Day 21 to Day 17.
  - User clicks the **"Simulate Factoring Advance"** toggle:
    - Cash buffer lifts by BDT 102,000.
    - Shortfall disappears; runway extends to 68 days.
- **Voiceover Narration:**
  > "In the Forecast Studio, the CFO can stress-test operating assumptions in real time. Sliding debtor delays pushes the shortfall 4 days earlier. But toggling an invoice factoring advance instantly rescues the runway, extending working capital by over two months. Every calculation is performed by deterministic NumPy routines—guaranteeing zero mathematical hallucination."

---

### [02:00 – 02:45] Phase 4: Financing Matching & "Why-Not" X-Ray Diagnostics
- **Visual:**
  - User navigates to `/financing`.
  - Top banner displays financial covenants:
    - **DSCR:** 1.18x (CMSME requirement: $\ge 1.25\text{x}$ — **FAIL**).
    - **Quick Ratio:** 3.94x (Pass).
    - **Leverage:** 1.61x (Pass).
  - Scheme list shows 2 Eligible schemes and 3 Ineligible schemes.
  - User clicks the **"Why Not? (X-Ray)"** button on the *CMSME Working Capital Scheme 2026*.
  - A sliding drawer opens displaying:
    - **Failed Criterion:** Debt Service Coverage Ratio (1.18x vs 1.25x required).
    - **Gap Analysis:** Shortfall of 0.07x in operating coverage.
    - **Actionable Remediation:** *"Pay down BDT 3,200 in current accounts payable to elevate DSCR to 1.26x."*
    - **Required Documentation Checklist:** Audited P&L, 6-Month Bank Statement, VAT Challan 6.3.
- **Voiceover Narration:**
  > "Instead of generic loan lists, AuraCFO provides mathematical Why-Not diagnostics. When evaluating the central bank's CMSME Working Capital Scheme, the system pinpoints why Bengal Craft was rejected: its DSCR is 1.18x versus the 1.25x regulatory hurdle. Crucially, it tells the owner exactly what to do: clear just 3,200 Taka in current accounts payable to cross the eligibility threshold."

---

### [02:45 – 03:30] Phase 5: Operations & Autonomy Tier Enforcement (T2 to T4)
- **Visual:**
  - User switches to `/operations` tab.
  - Aging accounts receivable table shows overdue invoice INV-2026-004 (Apex Retailers, BDT 120,000).
  - User clicks **"Draft Notice"** (Tier 2 Action).
  - The Collection Notice Drawer opens:
    - User selects Tone: **"Firm"**.
    - Notice text populates with factual balance amounts, due dates, and bank details.
  - User clicks **"Queue for Execution"** (Tier 4 Gate).
  - A prompt modal appears: *"T4 Action: Requires Cryptographic Owner Sign-Off. Added to Governance Approval Inbox."*
- **Voiceover Narration:**
  > "Under our T0 through T4 autonomy model, the AI can independently analyze data and draft collection communications at Tier 2. However, any legally binding action or dispatch of notices is classified as Tier 4, strictly requiring Human-In-The-Loop cryptographic approval. The notice cannot be sent autonomously—it is queued in the owner's approval inbox."

---

### [03:30 – 04:15] Phase 6: Governance, PII Diff & The Live Tamper Simulator
- **Visual:**
  - User navigates to `/governance`.
  - Three sections shown:
    1. **T4 Pending Approvals:** User reviews the queued notice and clicks **"Sign & Execute"**. The action executes with single-use cryptographic token validation.
    2. **PII Redaction Diff:** Displays original vs HMAC-SHA-256 tokens (`Apex Retailers` $\rightarrow$ `VEND-8f4b`), proving raw customer data never leaves the local vault.
    3. **SHA-256 Audit Trail:** Shows sequential block entries. Verification badge shows **"Status: Clean (Green)"**.
  - **The Winning Demo Moment:**
    - User clicks the **"Inject Synthetic Tamper"** button on the `TamperSimulatorBar`.
    - Instantly, the hash chain check recalculates in the browser: Block #2 turns crimson, and a warning banner screams: *"Tamper Detected at Block #2! Hash mismatch."*
    - User clicks **"Restore Chain"**, and the ledger immediately returns to valid green state.
- **Voiceover Narration:**
  > "In the Governance tab, judges can inspect our cryptographic guarantees. Notice how the PII vault masks all vendor names into HMAC-salted tokens before AI processing. Every action is sealed into a SHA-256 hash-chained Merkle ledger. Watch what happens when we simulate a database tampering event: the audit chain immediately detects the altered block and flags the breach in real time. Fraud is mathematically impossible to conceal."

---

### [04:15 – 04:30] Phase 7: Conclusion & Evaluation Summary
- **Visual:**
  - Floating Copilot Drawer opens on the right side.
  - User inputs: *"What is my recommended course of action for today?"*
  - SSE thought stream displays: *Analyzing 13-week runway... Verifying factoring eligibility...*
  - Copilot responds with a concise, verified 3-step action plan.
  - Closing splash screen shows GitHub repo URL, Docker command, and documentation package links.
- **Voiceover Narration:**
  > "AuraCFO bridges the divide between cutting-edge autonomous agents and the rigorous mathematical reliability demanded by institutional finance. Fast, secure, transparent, and completely verifiable. Thank you."
