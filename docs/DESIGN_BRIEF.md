# AuraCFO — Design Brief
## FinTechathon 2026 · Topic E · SME Finance Copilot

> **Version:** 1.0 · **Date:** 2026-10-14 · **Status:** LOCKED FOR BUILD
> **Purpose:** Single source of truth for every visual decision. Coding agents read this before touching any `.tsx` or `.css` file.
> **Reference Products:** Mercury Bank · Ramp · Linear · Brex (clean, dense, dark-mode, enterprise-grade)

---

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [Design Tokens (CSS Variables)](#2-design-tokens)
3. [Typography Scale](#3-typography-scale)
4. [Spacing & Layout Scale](#4-spacing--layout-scale)
5. [Color System & Semantic Meanings](#5-color-system--semantic-meanings)
6. [Border, Radius & Shadow](#6-border-radius--shadow)
7. [Responsive Breakpoints](#7-responsive-breakpoints)
8. [Animation & Transition Rules](#8-animation--transition-rules)
9. [Accessibility Requirements](#9-accessibility-requirements)
10. [5-State Component Matrix](#10-5-state-component-matrix)
11. [Component Anatomy Specs](#11-component-anatomy-specs)
12. [Page Layout Specs](#12-page-layout-specs)
13. [Tailwind Preset Configuration](#13-tailwind-preset-configuration)

---

## 1. Design Philosophy

| Principle | Rule |
|---|---|
| **Real product, not Dribbble** | Every screen must work with real data densities, real error states, real edge cases. No decorative-only elements |
| **Dark-mode only** | No light mode. Reduces scope, sharpens brand identity, matches reference products |
| **Density over decoration** | Use Linear/Mercury density — `py-2.5 px-3` for table cells, `p-4` for cards. No excessive whitespace |
| **Semantic color only** | Green = solvent/pass. Red = deficit/fail. Amber = warning/risk. Indigo = AI/agent. Blue = brand/action. Never use color decoratively |
| **Numbers are sacred** | All financial figures use `font-mono`. Currency formatting uses `formatCurrency()`. No raw `toFixed()` |
| **States before polish** | Implement loading/empty/error states BEFORE pixel-perfecting the default state |
| **Offline-safe assets** | Zero external font/icon/CDN requests. Everything bundled in `/public/fonts/` and `npm` |

---

## 2. Design Tokens

These tokens are the **single source of truth**. They live in `frontend/src/design-tokens/tokens.css` and must never be overridden with inline hex values anywhere in the codebase.

```css
:root {
  /* ─── Surfaces ─── */
  --bg-app: #090A0F;              /* Ultra-dark canvas (body background) */
  --bg-surface: #11131A;          /* Elevated cards, panels, sidebar */
  --bg-surface-hover: #171B26;    /* Hover state for rows, cards, nav items */
  --bg-subtle: #1C2130;           /* Inset containers, input fields, code blocks */

  /* ─── Borders ─── */
  --border-subtle: #1E2333;       /* Card outlines, dividers, table borders */
  --border-focus: #3B82F6;        /* Active input ring (brand blue) */

  /* ─── Typography ─── */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  --text-primary: #F8FAFC;        /* Headers, hero metrics (slate-50) */
  --text-secondary: #94A3B8;      /* Body copy, labels (slate-400) */
  --text-muted: #64748B;          /* Captions, inactive tabs, timestamps (slate-500) */

  /* ─── Semantic Financial Accents ─── */
  --color-solvency: #10B981;      /* Emerald-500 → positive cash, qualified, pass */
  --color-shortfall: #EF4444;     /* Red-500 → cash deficit, rejected, fail */
  --color-warning: #F59E0B;       /* Amber-500 → high delay risk, nearing covenant breach */
  --color-agent: #6366F1;         /* Indigo-500 → copilot thoughts, AI actions, agent borders */
  --color-brand: #2563EB;         /* Blue-600 → primary CTAs, links, active nav */

  /* ─── Derived Surface Accents (10% opacity overlays) ─── */
  --color-solvency-surface: rgba(16, 185, 129, 0.10);
  --color-shortfall-surface: rgba(239, 68, 68, 0.10);
  --color-warning-surface: rgba(245, 158, 11, 0.10);
  --color-agent-surface: rgba(99, 102, 241, 0.10);
  --color-brand-surface: rgba(37, 99, 235, 0.10);
}
```

### Usage Rules

| Token | Use For | Never Use For |
|---|---|---|
| `--bg-app` | `<body>`, page background | Card backgrounds |
| `--bg-surface` | Cards, panels, sidebar, modals, drawers | Page background |
| `--bg-surface-hover` | Row hover, card hover, nav item hover | Default state |
| `--bg-subtle` | Input fields, code blocks, inset containers | Card backgrounds |
| `--color-solvency` | Cash surplus, scheme eligible, covenant pass | Decorative green |
| `--color-shortfall` | Cash deficit, scheme rejected, covenant fail, critical alerts | Decorative red |
| `--color-warning` | Delay risk badges, warning alerts, "may be stale" | Decorative amber |
| `--color-agent` | Thought stream borders, agent avatars, AI attribution | Brand actions |
| `--color-brand` | Buttons, links, active nav indicator, focus rings | Status indicators |

---

## 3. Typography Scale

All fonts are bundled locally as variable `.woff2` files in `/public/fonts/`. **Zero Google Fonts requests.**

| Level | Tailwind Classes | Use Case | Font |
|---|---|---|---|
| **Hero Number** | `text-3xl font-semibold tracking-tight font-mono` | Metric card main value ($48,200) | JetBrains Mono |
| **Hero Number (overflow)** | `text-2xl font-semibold tracking-tight font-mono` | Values > 8 digits (৳142,500,000) | JetBrains Mono |
| **Page Title** | `text-xl font-semibold text-slate-50` | "Executive Dashboard", "Forecast Studio" | Inter |
| **Card Title** | `text-xs font-medium uppercase tracking-wider text-slate-400` | "CASH RUNWAY", "PENDING APPROVALS" | Inter |
| **Section Header** | `text-sm font-semibold text-slate-200` | Region headers within a page | Inter |
| **Body Text** | `text-sm text-slate-200 font-sans` | Paragraphs, descriptions | Inter |
| **Label** | `text-xs text-slate-400` | Form labels, axis labels | Inter |
| **Table Cell** | `text-sm text-slate-200 font-sans` | Data table content | Inter |
| **Table Header** | `text-xs font-medium uppercase tracking-wider text-slate-400` | Column headers | Inter |
| **Code / Hash** | `text-xs font-mono text-slate-300` | Audit hashes, API responses | JetBrains Mono |
| **Badge** | `text-xs font-medium` | Status badges (ELIGIBLE, OVERDUE) | Inter |
| **Button (primary)** | `text-sm font-medium` | CTA buttons | Inter |
| **Button (secondary)** | `text-sm font-normal text-slate-300` | Secondary actions | Inter |
| **Caption / Timestamp** | `text-xs text-slate-500` | "Updated 2 min ago", block timestamps | Inter |

### Font Loading

```css
/* In tokens.css — loaded BEFORE any component renders */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/Inter-Variable.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
}
@font-face {
  font-family: 'JetBrains Mono';
  src: url('/fonts/JetBrainsMono-Variable.woff2') format('woff2-variations');
  font-weight: 100 800;
  font-display: swap;
}
```

---

## 4. Spacing & Layout Scale

### Spacing Tokens

| Name | Value | Use Case |
|---|---|---|
| `space-1` | `4px` (`p-1`) | Icon padding, tight inline gaps |
| `space-2` | `8px` (`p-2`) | Between badge and text, compact gaps |
| `space-2.5` | `10px` (`py-2.5`) | Table row vertical padding |
| `space-3` | `12px` (`p-3`, `px-3`) | Table cell horizontal padding, input padding |
| `space-4` | `16px` (`p-4`) | Standard card internal padding |
| `space-5` | `20px` (`p-5`) | Large card padding |
| `space-6` | `24px` (`p-6`, `gap-6`) | Grid gap between cards |
| `space-8` | `32px` (`p-8`) | Page section spacing |

### Layout Widths

| Element | Width | Rule |
|---|---|---|
| Sidebar | `w-[240px]` fixed | Always visible on desktop. Collapsible to `w-[64px]` icons-only |
| Topbar | Full width minus sidebar | `h-[56px]` fixed |
| Content area | Remaining width | `max-w-[1400px]` centered with `mx-auto` |
| Copilot Drawer | `w-[400px]` fixed | Right-aligned, z-50. Content area shrinks when open |
| Why-Not Drawer | `w-[480px]` fixed | Slides over Copilot Drawer (z-[60]) |
| Modal (confirmation) | `max-w-[480px]` | Centered, z-[100], backdrop blur |

### Grid System

| Context | Grid | Gap |
|---|---|---|
| Hero metric cards (Dashboard) | `grid grid-cols-4` | `gap-6` |
| Scheme cards (Financing) | `grid grid-cols-2` | `gap-6` |
| Aging buckets (Operations) | `grid grid-cols-4` | `gap-4` |
| Benchmark cards (Data) | `grid grid-cols-2` | `gap-6` |
| Responsive: < 1024px | `grid-cols-2` for 4-col → 2-col | Same gap |
| Responsive: < 768px | `grid-cols-1` | Same gap |

---

## 5. Color System & Semantic Meanings

### Primary Semantic Palette

| Color | Token | Hex | Meaning | Used On |
|---|---|---|---|---|
| Solvency Green | `--color-solvency` | `#10B981` | Cash healthy, covenant pass, scheme eligible | Metric badge, covenant gauge fill, scheme card border |
| Shortfall Red | `--color-shortfall` | `#EF4444` | Cash deficit, covenant fail, rejection, critical alert | Shortfall date label, failed covenant, 60+ aging bucket |
| Warning Amber | `--color-warning` | `#F59E0B` | High delay risk, approaching threshold, stale data | P(delay) badge > 60%, DSCR nearing threshold, ⚠️ stale scheme |
| Agent Indigo | `--color-agent` | `#6366F1` | AI is acting, copilot attribution, thought traces | Thought stream left border, agent avatar ring, tool call cards |
| Brand Blue | `--color-brand` | `#2563EB` | User actions, interactive controls, navigation | Primary buttons, links, active sidebar indicator, focus ring |

### Badge Color Map

| Badge Text | Background | Text Color | Border |
|---|---|---|---|
| ELIGIBLE | `bg-emerald-500/10` | `text-emerald-400` | `border-emerald-500/20` |
| INELIGIBLE | `bg-red-500/10` | `text-red-400` | `border-red-500/20` |
| OVERDUE | `bg-red-500/10` | `text-red-400` | `border-red-500/20` |
| HIGH RISK | `bg-amber-500/10` | `text-amber-400` | `border-amber-500/20` |
| MEDIUM RISK | `bg-amber-500/10` | `text-amber-300` | `border-amber-500/20` |
| LOW RISK | `bg-emerald-500/10` | `text-emerald-400` | `border-emerald-500/20` |
| PENDING | `bg-amber-500/10` | `text-amber-400` | `border-amber-500/20` |
| APPROVED | `bg-emerald-500/10` | `text-emerald-400` | `border-emerald-500/20` |
| REJECTED | `bg-red-500/10` | `text-red-400` | `border-red-500/20` |
| CRITICAL | `bg-red-500/15` | `text-red-300` | `border-red-500/30` |
| WARNING | `bg-amber-500/15` | `text-amber-300` | `border-amber-500/30` |
| INFO | `bg-blue-500/10` | `text-blue-400` | `border-blue-500/20` |
| T0–T4 | `bg-indigo-500/10` | `text-indigo-400` | `border-indigo-500/20` |
| VERIFIED ✅ | `bg-emerald-500/10` | `text-emerald-400` | — |
| TAMPERED ❌ | `bg-red-500/15` | `text-red-300` | `border-red-500/30` |

### Chart Color Assignments

| Chart Element | Color | Tailwind | Purpose |
|---|---|---|---|
| P90 (optimistic band) | `#10B981` opacity 0.15 | `fill-emerald-500/15` | Upper confidence |
| P50 (median line) | `#F8FAFC` | `stroke-slate-50` | Primary forecast |
| P10 (pessimistic band) | `#EF4444` opacity 0.15 | `fill-red-500/15` | Lower confidence |
| Safety floor line | `#F59E0B` dashed | `stroke-amber-500` | Minimum reserve threshold |
| Baseline curve | `#F8FAFC` solid | `stroke-slate-50` | Reference forecast |
| Stressed scenario | `#EF4444` dashed | `stroke-red-500` | What-if stressed |
| Factoring overlay | `#10B981` dashed | `stroke-emerald-500` | With factoring applied |
| Inflow bars | `#10B981` | `fill-emerald-500` | Weekly inflows |
| Outflow bars | `#EF4444` | `fill-red-500` | Weekly outflows |

---

## 6. Border, Radius & Shadow

| Element | Border | Radius | Shadow |
|---|---|---|---|
| Card (default) | `border border-[var(--border-subtle)]` | `rounded-lg` (8px) | None (flat cards, Mercury-style) |
| Card (hover) | Same border | Same radius | `shadow-sm` subtle lift |
| Card (error state) | `border-red-500/30` | Same | None |
| Input field | `border border-[var(--border-subtle)]` | `rounded-md` (6px) | None |
| Input (focused) | `ring-2 ring-[var(--border-focus)]` | Same | None |
| Button (primary) | None | `rounded-md` (6px) | None |
| Button (secondary) | `border border-[var(--border-subtle)]` | `rounded-md` | None |
| Badge | None | `rounded-full` (pill) | None |
| Table | `border border-[var(--border-subtle)]` | `rounded-lg` (outer container) | None |
| Modal / Dialog | `border border-[var(--border-subtle)]` | `rounded-xl` (12px) | `shadow-2xl` |
| Drawer | `border-l border-[var(--border-subtle)]` | None (flush to edge) | `shadow-2xl` |
| Tooltip | None | `rounded-md` | `shadow-lg` |
| Toast | `border border-[var(--border-subtle)]` | `rounded-lg` | `shadow-lg` |

**Rule: No `shadow-*` on flat page cards.** Only modals, drawers, tooltips, and toasts get shadows. Mercury-style flat card density.

---

## 7. Responsive Breakpoints

| Breakpoint | Width | Layout Changes |
|---|---|---|
| `xl` (default) | ≥ 1280px | Full sidebar (240px) + content + drawer (400px) |
| `lg` | ≥ 1024px | Full sidebar + content. Drawer overlays content |
| `md` | ≥ 768px | Collapsed sidebar (64px, icons only). 4-col grids → 2-col |
| `sm` | < 768px | No sidebar (hamburger menu). 2-col grids → 1-col. Drawer is full-screen overlay. No side-by-side chart+controls — stack vertically |

### Specific Responsive Rules

| Component | Desktop (≥ 1024px) | Mobile (< 768px) |
|---|---|---|
| Forecast page | Left rail 30% + right chart 70% (side by side) | Stacked: controls top, chart below |
| Financing page | 2-column scheme grid | 1-column stack |
| Copilot Drawer | 400px fixed right panel | Full-screen overlay |
| Hero metric cards | 4 columns | 2 columns, then 1 on < 480px |
| Invoice table | Full columns visible | Horizontal scroll with sticky first column |

---

## 8. Animation & Transition Rules

| Element | Animation | Duration | Easing |
|---|---|---|---|
| Page transition | None (instant route swap) | — | — |
| Card hover | Background color change | `150ms` | `ease-out` |
| Drawer open/close | Slide from right edge | `200ms` | `ease-in-out` |
| Modal appear | Scale from 95% + fade in | `150ms` | `ease-out` |
| Modal disappear | Scale to 95% + fade out | `100ms` | `ease-in` |
| Shimmer skeleton | Left-to-right gradient sweep | `1.5s` | `linear` (infinite) |
| Toast appear | Slide down from top-right | `200ms` | `ease-out` |
| Toast disappear | Fade out | `150ms` | `ease-in` |
| Metric card value update | Number counter (animate from old → new) | `500ms` | `ease-out` |
| Chart data update | Line/bar morph (Recharts `animationDuration`) | `500ms` | `ease-out` |
| Badge status change | Color cross-fade | `200ms` | `ease-out` |
| Approval card: Pending → Approved | Border color green + checkmark icon scale-in | `300ms` | `ease-out` |

**Rule: No spring physics, no bounce, no parallax.** This is a financial product — animations should be fast and understated.

---

## 9. Accessibility Requirements

### Contrast (WCAG AA minimum)

| Text | Background | Contrast Ratio | Pass? |
|---|---|---|---|
| `--text-primary` (#F8FAFC) | `--bg-surface` (#11131A) | 17.2:1 | ✅ AAA |
| `--text-secondary` (#94A3B8) | `--bg-surface` (#11131A) | 7.1:1 | ✅ AA |
| `--text-muted` (#64748B) | `--bg-surface` (#11131A) | 4.6:1 | ✅ AA |
| `--color-solvency` (#10B981) | `--bg-surface` (#11131A) | 8.4:1 | ✅ AA |
| `--color-shortfall` (#EF4444) | `--bg-surface` (#11131A) | 5.1:1 | ✅ AA |
| `--color-warning` (#F59E0B) | `--bg-surface` (#11131A) | 8.9:1 | ✅ AA |

### Keyboard Navigation

| Requirement | Implementation |
|---|---|
| All interactive elements focusable | Tab order follows visual reading order |
| Focus ring visible | `ring-2 ring-[var(--border-focus)] ring-offset-2 ring-offset-[var(--bg-surface)]` |
| Escape closes modals/drawers | `onKeyDown` handler on modal/drawer root |
| Enter activates buttons | Default HTML behavior preserved |
| Arrow keys in tables | Optional (nice-to-have) |
| Cmd/Ctrl + K opens Copilot | Global keyboard shortcut |

### Screen Reader

| Requirement | Implementation |
|---|---|
| Metric cards have `aria-label` | `aria-label="Cash runway: 34 days"` |
| Chart has `aria-label` with summary | `aria-label="13-week forecast showing shortfall on November 4"` |
| Status badges have `aria-label` | `aria-label="Status: eligible"` |
| Loading states announce | `aria-live="polite"` on shimmer containers |
| Alert severity announced | `role="alert"` on critical/warning alert cards |

---

## 10. 5-State Component Matrix

**Every data-display component MUST implement all 5 states.** This is what judges click to break — they load empty data, trigger errors, and paste long values.

| Component | Default | Loading | Empty | Error | Long-Value |
|---|---|---|---|---|---|
| **MetricCard** | Value + trend + badge | Shimmer `h-[96px]` | "—" with muted label | Red border + "Failed" + `[Retry]` | Font scales `text-2xl` + tooltip |
| **QuantileForecastChart** | P10/P50/P90 ribbons | Shimmer `h-[340px]` | "No forecast data. Load data first." + CTA | Error overlay + `[Retry]` | N/A (chart auto-scales) |
| **AlertFeed** | Severity-ranked cards | Shimmer × 3 cards | "No alerts — your finances look healthy ✅" | "Could not load alerts" + `[Retry]` | Alert text truncates with `line-clamp-2` + expand |
| **InvoiceTable** | Sortable data rows | Shimmer rows × 5 | "No invoices found" + CTA | Error banner above table | Amount column: `text-sm` + tooltip for > 10 chars |
| **SchemeCard** | Scheme info + CTA | Shimmer card | "No schemes available" | "Matching failed" + `[Retry]` | Scheme name: `line-clamp-1` + tooltip |
| **CovenantGauge** | Value + threshold + badge | Shimmer gauge | "Compute covenants first" | "Error" badge | Value auto-formats (1.18x → fits) |
| **WhyNotDrawer** | Rules + remediation | Shimmer list | "No failures found" | "Failed to load details" | Steps truncate with "Show more" |
| **AuditTrailTable** | Hash chain rows | Shimmer rows × 10 | "No audit entries yet" | "Could not load trail" | Hash truncates to 8 chars + copy button |
| **ApprovalCard** | Payload + Approve/Reject | Shimmer card | "No pending approvals ✅" | "Failed to load" | Payload preview: `max-h-[200px]` + scroll |
| **CopilotDrawer** | Chat history + input | "Thinking..." shimmer | Welcome message | "Could not connect" + `[Retry]` | Messages scroll, input has maxLength |
| **ThoughtStream** | Collapsible thought cards | Animated shimmer line | N/A (part of drawer) | "Step failed" badge per thought | Text truncates with expand toggle |
| **BenchmarkSeeder** | 2 scenario cards + CTA | Spinner on active card | N/A (always shows cards) | "Seeding failed" + `[Retry]` | N/A |
| **FileDropzone** | Dashed border + label | Spinner + progress | Default IS idle state | "Upload failed: {reason}" | File name truncates with tooltip |
| **PIIRedactionDiff** | Side-by-side diff | Shimmer | "No PII detected" | "Failed to load" | Long entity names wrap |

---

## 11. Component Anatomy Specs

### MetricCard

```
┌─────────────────────────────────────┐
│  CASH RUNWAY                   ▲ 12%│  ← Card title (text-xs uppercase) + trend
│                                     │
│  34 days                            │  ← Hero value (text-3xl font-mono)
│  Shortfall: Nov 04                  │  ← Sub-label (text-xs text-slate-400)
│                                     │
│  ████████████░░░░  78%              │  ← Optional progress bar
└─────────────────────────────────────┘
  Padding: p-4
  Border: border border-[var(--border-subtle)] rounded-lg
  Height: h-[96px] (fixed for shimmer matching)
  Status color: left-4 border-l-2 (green/amber/red)
```

### SchemeCard

```
┌─────────────────────────────────────────────┐
│  ✅ ELIGIBLE                    Match: 98%   │  ← Badge (emerald) + score
│                                              │
│  CMSME Working Capital Fund                  │  ← Scheme name (text-sm font-semibold)
│  Bangladesh Bank                             │  ← Issuer (text-xs text-slate-400)
│                                              │
│  Rate: 9.0%   Max: ৳25L   Tenure: 12mo      │  ← Key terms row
│                                              │
│  [Prepare Application (T3)]                  │  ← Primary CTA
└─────────────────────────────────────────────┘
  Eligible border: border-emerald-500/30
  Ineligible border: border-red-500/20, opacity-75
  Ineligible has [Why Not?] instead of [Prepare Application]
  Stale scheme (>180 days): ⚠️ badge in top-right
```

### ApprovalCard

```
┌──────────────────────────────────────────────┐
│  🔒 PENDING APPROVAL                         │  ← Status badge (amber)
│                                               │
│  Send Collection Email to Bashundhara Paper   │  ← Action summary
│  Invoice #INV-1082 · $6,400                   │  ← Context
│  Initiated by: Treasurer Agent                │  ← Agent attribution
│  Requested: 2 min ago                         │  ← Timestamp
│                                               │
│  [Review Details ▼]                           │  ← Expand to show full payload
│                                               │
│  [Reject]                    [Approve ✅]      │  ← Action buttons
└──────────────────────────────────────────────┘
  Pending: border-amber-500/20
  Approved: border-emerald-500/20 + ✅ badge replaces buttons
  Rejected: border-red-500/20 + ❌ badge + reason shown
```

### CopilotDrawer

```
┌──────────────────────────────────────────┐  w-[400px], z-50
│  AuraCFO Assistant    [Owner ▼]   [✕]    │  ← Header: title + persona toggle + close
├──────────────────────────────────────────┤
│  ▼ 1. Checking input for threats... ✅    │  ← ThoughtStream (collapsible)
│  ▼ 2. Running Monte Carlo (1000 runs)... │     agent-indigo left border
│  ▼ 3. 🔧 forecast_cash() → 13 weeks     │     tool calls show as cards
├──────────────────────────────────────────┤
│  "You have 34 days of cash runway...     │  ← Synthesis message
│   The shortfall on Nov 04 can be offset  │     bg-surface, rounded-lg, p-4
│   by invoice factoring."                 │
├──────────────────────────────────────────┤
│  [Prepare Factoring] [Draft Reminder]    │  ← ActionChips
├──────────────────────────────────────────┤
│  [Ask AuraCFO anything...         ] [➤]  │  ← ChatInput
└──────────────────────────────────────────┘
  Thoughts: border-l-2 border-indigo-500, bg-indigo-500/5
  Synthesis: bg-surface, text-slate-200
  User messages: bg-brand/10, right-aligned
  Action chips: bg-surface-hover, border, rounded-full, text-sm
```

### CovenantGauge

```
┌──────────────────────────────────┐
│  DSCR                      ⚠️    │  ← Label + status icon
│                                  │
│  1.18x                           │  ← Current value (font-mono, text-xl)
│  Required: ≥ 1.25x               │  ← Threshold (text-xs text-slate-400)
│                                  │
│  ██████████████░░░░  94%         │  ← Progress bar (value/threshold)
│                                  │     < 100%: amber. ≥ 100%: green
└──────────────────────────────────┘
  Pass: border-emerald-500/20, progress fill emerald
  Fail: border-amber-500/20, progress fill amber
  Critical fail (< 80%): border-red-500/20, progress fill red
```

---

## 12. Page Layout Specs

### Dashboard (`/dashboard`)

```
┌─────────────────────────────────────────────────────────────┐
│  Topbar                                                      │
├──────────┬──────────────────────────────────────────────────┤
│          │  [MetricCard] [MetricCard] [MetricCard] [MetricCard]│  4-col grid, gap-6
│ Sidebar  │                                                    │
│  240px   │  ┌────────────────────────────┬───────────────────┐│
│          │  │ QuantileForecastChart      │ AlertFeed         ││  65% / 35%
│          │  │ h-[340px]                  │ max-h-[340px]     ││
│          │  │ P10/P50/P90 ribbons        │ scroll-y          ││
│          │  └────────────────────────────┴───────────────────┘│
│          │                                                    │
│          │  InvoiceTable (full width)                          │
│          │  Receivables summary table                         │
└──────────┴──────────────────────────────────────────────────┘
```

### Forecast (`/forecast`)

```
┌──────────┬──────────────────────────────────────────────────┐
│          │  ┌────────────────┬───────────────────────────────┐│
│ Sidebar  │  │ ScenarioControls│ ScenarioComparisonChart      ││  30% / 70%
│          │  │ (Left Rail)    │ Baseline + stressed overlay   ││
│          │  │                │ h-[400px]                     ││
│          │  │ 4 Presets      │                               ││
│          │  │ 3 Sliders      │ CashFlowBarChart              ││
│          │  │ 1 Toggle       │ (weekly inflow/outflow)       ││
│          │  │ Reset button   │                               ││
│          │  └────────────────┴───────────────────────────────┘│
│          │                                                    │
│          │  DebtorHazardTable (full width)                     │
└──────────┴──────────────────────────────────────────────────┘
```

### Financing (`/financing`)

```
┌──────────┬──────────────────────────────────────────────────┐
│          │  CovenantMonitor (full width banner)               │
│ Sidebar  │  [DSCR gauge] [QR gauge] [Leverage gauge] [Burn]  │  4-col grid
│          │                                                    │
│          │  ┌───────────────────────┬────────────────────────┐│
│          │  │ Eligible Schemes      │ Ineligible Schemes     ││  50% / 50%
│          │  │ SchemeCard[] (green)   │ SchemeCard[] (dimmed)  ││
│          │  └───────────────────────┴────────────────────────┘│
│          │                                                    │
│          │  [WhyNotDrawer slides in from right on click]      │
└──────────┴──────────────────────────────────────────────────┘
```

---

## 13. Tailwind Preset Configuration

```typescript
// frontend/src/design-tokens/tailwind-preset.ts
import type { Config } from "tailwindcss";

const preset: Partial<Config> = {
  theme: {
    extend: {
      colors: {
        "bg-app": "var(--bg-app)",
        "bg-surface": "var(--bg-surface)",
        "bg-surface-hover": "var(--bg-surface-hover)",
        "bg-subtle": "var(--bg-subtle)",
        "border-subtle": "var(--border-subtle)",
        "border-focus": "var(--border-focus)",
        solvency: "var(--color-solvency)",
        shortfall: "var(--color-shortfall)",
        warning: "var(--color-warning)",
        agent: "var(--color-agent)",
        brand: "var(--color-brand)",
      },
      fontFamily: {
        sans: ["var(--font-sans)"],
        mono: ["var(--font-mono)"],
      },
      borderRadius: {
        lg: "8px",   // Cards
        md: "6px",   // Inputs, buttons
        xl: "12px",  // Modals
      },
      width: {
        sidebar: "240px",
        "sidebar-collapsed": "64px",
        drawer: "400px",
        "whynot-drawer": "480px",
      },
      height: {
        topbar: "56px",
        "metric-card": "96px",
        "chart-main": "340px",
        "chart-forecast": "400px",
      },
      zIndex: {
        drawer: "50",
        "whynot-drawer": "60",
        modal: "100",
        toast: "110",
      },
      animation: {
        shimmer: "shimmer 1.5s linear infinite",
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
};

export default preset;
```
