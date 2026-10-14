# AuraCFO — Technical Requirements Document (TRD)
## FinTechathon 2026 · Topic E · SME Finance Copilot

> **Version:** 1.1 · **Date:** 2026-10-14 · **Status:** PATCHED & VERIFIED FOR BUILD
> **Companion to:** PRD.md (what to build) → this doc (how to build it)

---

## 1. Technology Stack — Exact Versions

### Backend

| Layer | Technology | Version | Why This Choice |
|---|---|---|---|
| Language | Python | 3.12+ | LangGraph + ML ecosystem |
| Package Manager | uv | latest | 10x faster than pip; reproducible lockfile |
| Web Framework | FastAPI | 0.115+ | Async, OpenAPI auto-docs, SSE support, Pydantic v2 |
| ASGI Server | Uvicorn | 0.30+ | Production-grade async server |
| ORM | SQLAlchemy | 2.0+ | Async support, type hints, declarative models |
| Migrations | Alembic | 1.13+ | Schema versioning for reproducible DB setup |
| Agent Framework | LangGraph | 0.2+ | StateGraph, checkpoints, `interrupt()` for HITL, time-travel replay |
| LLM Client | LiteLLM | 1.50+ | Unified interface: OpenAI/Anthropic/Gemini/Ollama behind one API |
| ML Forecasting | XGBoost | 2.1+ | Payment delay classifier |
| Numerics | pandas 2.2+, numpy 2.0+, scikit-learn 1.5+ | Deterministic engines |
| PII Detection | regex + deterministic NER rules | stdlib | Offline-safe PII scrubbing (zero HuggingFace runtime downloads behind GFW) |
| Hashing | hashlib (stdlib) | — | SHA-256 for audit chain |
| HMAC Tokens | hmac (stdlib) | — | Deterministic PII token generation |
| MCP Server | mcp (Anthropic SDK) | 1.0+ | Model Context Protocol server (stretch) |
| Testing | pytest 8+, pytest-asyncio, httpx | — | Async test support + API test client |

### Frontend

| Layer | Technology | Version | Why This Choice |
|---|---|---|---|
| Language | TypeScript | 5.5+ | Type safety prevents data shape bugs |
| Framework | React | 19 | Latest concurrent features |
| Build Tool | Vite | 6+ | Sub-second HMR; production builds in < 10s |
| Styling | Tailwind CSS | 3.4+ | Utility-first; design tokens via CSS variables |
| Component Library | shadcn/ui | latest | Copy-paste components; full ownership of code |
| Charts | Recharts | 2.12+ | Composable React chart components (SSR-safe) |
| Chart Gauges | shadcn/ui + Recharts | latest | Custom CovenantGauge & MetricCard components (avoids Tremor React 18 peer-dep conflict with React 19) |
| Routing | React Router | 6.x | Nested routes, lazy loading |
| Data Fetching | @tanstack/react-query | 5+ | Caching, background revalidation, polling |
| SSE Streaming | Native EventSource | — | No extra dependency needed |
| Utilities | clsx + tailwind-merge | — | Conditional class merging |
| Icons | Lucide React | latest | Tree-shakable, bundled (no CDN) |
| Fonts | Inter + JetBrains Mono | Variable | Bundled .woff2 in /public/fonts/ |

### Infrastructure

| Layer | Technology | Version | Why This Choice |
|---|---|---|---|
| Containerization | Docker + Docker Compose | v2+ | Single-command deployment |
| Database (dev) | SQLite | 3.45+ | Zero-config for local dev |
| Database (prod/demo) | PostgreSQL | 17 | JSONB, pgvector support |
| Vector Store | pgvector (in Postgres) | 0.7+ | Embedding storage without extra service (stretch) |
| Process Manager | Docker Compose | v2 | Orchestrates backend + frontend + db |
| CI/CD | GitHub Actions | — | Run tests on push |

---

## 2. System Requirements

### Development Machine
- OS: Windows 10/11, macOS 12+, or Ubuntu 22.04+
- Python 3.12+
- Node.js 20+
- Docker Desktop 4.x+ with Docker Compose v2
- 8 GB RAM minimum (16 GB recommended for XGBoost + Monte Carlo)
- 10 GB free disk space (Docker images + dependencies)

### Judge/Demo Machine
- Docker Desktop installed (any OS)
- No other dependencies required — everything is containerized
- **No internet required** — MOCK_LLM auto-fallback handles offline mode

---

## 3. Backend Architecture Requirements

### 3.1 API Design Principles

| Principle | Rule |
|---|---|
| REST conventions | Resource-oriented URLs, proper HTTP methods, status codes |
| Schema validation | Every request/response validated via Pydantic models — no raw dicts |
| Error handling | All errors return `{"error": string, "detail": string, "code": string}` — never stack traces |
| Streaming | Chat endpoint uses SSE (Server-Sent Events), not WebSockets |
| Auth | Single-user demo — no auth middleware (but permission service enforces T0–T4 on tools) |
| CORS | Allow `http://localhost:3000` and `http://localhost:5173` (dev + prod) |
| Versioning | No API versioning needed for competition scope |

### 3.2 Deterministic Engine Rules (MANDATORY)

These rules are **non-negotiable** — violation breaks the core security thesis.

| Rule # | Rule | Enforcement |
|---|---|---|
| DE-01 | No engine file shall import `langchain`, `openai`, `anthropic`, `litellm`, or any LLM library | CI lint check |
| DE-02 | All financial calculations must use `decimal.Decimal` or `float64` with 2-place rounding at output | Unit tests verify precision |
| DE-03 | Monte Carlo must accept a `seed` parameter for reproducibility | Test: same seed = same output |
| DE-04 | Engine outputs must be pure dicts — no side-effects, no DB writes, no external calls | Code review + type hints |
| DE-05 | The LLM receives engine outputs as **read-only** tool results — it cannot modify them | Enforced in LangGraph node code |

### 3.3 Agent Architecture Rules

| Rule # | Rule |
|---|---|
| AG-01 | Each agent node is a separate Python file in `agents/` with a single entry function |
| AG-02 | Agent tool allowlists are enforced in code (dict lookup), not in prompts |
| AG-03 | Orchestrator (Virtual CFO) NEVER calls engines directly — it delegates to specialist agents |
| AG-04 | Risk Sentinel wraps every request as pre-flight (injection+PII) and post-flight (output validation) |
| AG-05 | All LangGraph state mutations go through `AgentState` TypedDict — no global state |
| AG-06 | T4 tools use LangGraph `interrupt()` — the graph pauses until human resumes via API |
| AG-07 | System prompts are frozen in `prompts.py` — no dynamic prompt assembly from user data |

### 3.4 Security Layer Rules

| Rule # | Rule |
|---|---|
| SEC-01 | PII sanitization runs BEFORE any data reaches the LLM — enforced in Risk Sentinel pre-flight |
| SEC-02 | Injection guard checks every text input: user chat, OCR output, bank narration, CSV fields |
| SEC-03 | Permission enforcement is a Python decorator on tool handlers — not a prompt instruction |
| SEC-04 | T4 tools raise `PermissionDenied` exception at code level — no soft "I'm sorry, I can't" |
| SEC-05 | Audit logger is called as a side-effect of every agent node — not optional |
| SEC-06 | Hash chain formula: `H_n = SHA-256(f"{previous_hash}|{timestamp_iso}|{agent_role}|{tool_name}|{input_hash}|{output_hash}")` |
| SEC-07 | Output validator asserts: every financial figure (currency amounts, percentages, covenant multipliers/ratios) in the LLM response matches a value in the deterministic tool result (whitelisting list ordinals `1.`, `2.`, dates, and standard horizon constants `13`, `30`, `60`, `90`) |

### 3.5 Offline / Mock Mode Rules

| Rule # | Rule |
|---|---|
| OFF-01 | On startup, backend pings LLM API with 5-second timeout. If fail → set `MOCK_LLM=true` automatically |
| OFF-02 | When `MOCK_LLM=true`, all deterministic engines run LIVE — only LLM narrative is mocked |
| OFF-03 | Mock responses are stored in `cached_traces.json` — not hardcoded in Python code |
| OFF-04 | Frontend must never request external fonts — all fonts bundled in `/public/fonts/` |
| OFF-05 | Frontend must never load scripts from CDN — all JS dependencies bundled via Vite |
| OFF-06 | Docker images must contain all dependencies — `docker compose up --build` must work offline after initial pull |

---

## 4. Frontend Architecture Requirements

### 4.1 Component Design Rules

| Rule # | Rule |
|---|---|
| FE-01 | Every data-display component must implement 5 states: Default, Loading (shimmer), Empty, Error, Long-Value |
| FE-02 | Design tokens (colors, spacing, radii, fonts) are defined in `tokens.css` and `tailwind-preset.ts` — never inline hex values |
| FE-03 | Currency formatting uses `formatCurrency(amount, currency)` utility — never raw `toFixed(2)` |
| FE-04 | Date formatting uses `formatDate(date)` utility — never raw `toLocaleDateString()` |
| FE-05 | All API calls go through typed hooks (`useApi`, `useForecast`, etc.) — never raw `fetch()` in components |
| FE-06 | Copilot Drawer is persistent across page navigation — it's rendered in `App.tsx`, not per-page |
| FE-07 | SSE events from `/api/chat` are typed: `thought`, `tool_call`, `tool_result`, `synthesis`, `error` |
| FE-08 | Scenario sliders debounce 300ms before triggering API calls |
| FE-09 | No page may call a write endpoint without showing confirmation — aligns with T2/T4 governance |

### 4.2 SSE Event Types (Frontend ↔ Backend contract)

```typescript
// SSE event stream from POST /api/chat
type SSEEvent =
  | { type: "thought"; agent: string; text: string }           // "Planning cash forecast..."
  | { type: "tool_call"; agent: string; tool: string; args: Record<string, unknown> }
  | { type: "tool_result"; agent: string; tool: string; result: Record<string, unknown> }
  | { type: "synthesis"; text: string; citations: string[] }   // Final narrative
  | { type: "approval_required"; approval_id: string; action_type: string }
  | { type: "error"; code: string; message: string }
  | { type: "done" }
```

### 4.3 Route → Page → API Mapping

| Route | Page Component | Primary API Calls | Data Hook |
|---|---|---|---|
| `/dashboard` | `DashboardPage.tsx` | `GET /api/dashboard/{cid}` | `useDashboard(cid)` |
| `/forecast` | `ForecastPage.tsx` | `POST /api/forecast`, `POST /api/scenario` | `useForecast(cid)`, `useScenario()` |
| `/financing` | `FinancingPage.tsx` | `GET /api/financing/{cid}` | `useFinancing(cid)` |
| `/operations` | `OperationsPage.tsx` | `GET /api/invoices/{cid}`, `POST /api/draft-collection` | `useInvoices(cid)` |
| `/governance` | `GovernancePage.tsx` | `GET /api/approvals/{cid}`, `GET /api/audit-trail/{cid}`, `POST /api/approve` | `useApprovals(cid)`, `useAuditTrail(cid)` |
| `/data` | `DataPage.tsx` | `POST /api/seed-benchmark`, `POST /api/ingest` | `useIngestion()` |
| Global Drawer | `CopilotDrawer.tsx` | `POST /api/chat` (SSE) | `useChat()` |

---

## 5. Database Requirements

### 5.1 Engine Choice Logic

```
if DATABASE_URL starts with "sqlite":
    use SQLite (dev/demo mode — zero config)
elif DATABASE_URL starts with "postgresql":
    use PostgreSQL 17 (production/Docker mode)
```

### 5.2 Migration Strategy

- All schema changes via Alembic migration files in `backend/alembic/versions/`
- On startup, backend runs `alembic upgrade head` automatically
- Migration files are committed to Git — reproducible DB state from any commit
- `make reset-db` = drop all tables + re-run all migrations + seed benchmark data

### 5.3 Data Integrity Rules

| Rule | Implementation |
|---|---|
| All primary keys are UUID4 | `uuid.uuid4()` generated in Python, not DB |
| All timestamps are UTC | `datetime.utcnow()` — never local time |
| PII is never stored in plaintext | Only HMAC tokens + SHA-256 hashes of originals |
| Audit entries are append-only | No UPDATE or DELETE allowed on `audit_entry` table |
| Approval records are immutable once resolved | Status transitions: pending → approved/rejected (one-way) |
| Scheme data lives in JSON files, not DB | Easier to audit, cite, version-control |

---

## 6. Testing Requirements

### 6.1 Test Categories

| Category | Location | Runner | Min Count | Gate |
|---|---|---|---|---|
| Unit tests (engines) | `tests/test_*_engine.py` | pytest | 20 | All pass |
| Unit tests (security) | `tests/test_injection_guard.py`, `test_pii_sanitizer.py`, `test_permission_service.py`, `test_audit_logger.py`, `test_output_validator.py` | pytest | 70 | ≥98% injection block rate |
| Integration tests (API) | `tests/test_api_integration.py` | pytest + httpx | 10 | All pass |
| E2E replay | `tests/replay_sandbox.py` | Python script | 1 (7 assertions) | All pass, JSONL output |

### 6.2 Test Data Requirements

| Dataset | File | Records | Purpose |
|---|---|---|---|
| Bengal Craft ledger | `data/bengal_craft_ledger.csv` | 128 transactions | Primary benchmark |
| Bengal Craft invoices | `data/bengal_craft_invoices.csv` | 56 invoices (48 historical paid + 8 active) | XGBoost delay model training + AR ledger |
| Shenzhen importer | `data/shenzhen_importer.csv` | ~50 transactions | Cross-border scenario (stretch) |
| Injection corpus | `data/injection_corpus/*.json` | 50+ payloads | Red-team security tests |

### 6.3 CI Pipeline

```yaml
# .github/workflows/test.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run pytest tests/ -v --tb=short
      - run: uv run python -m tests.replay_sandbox
```

---

## 7. Deployment Requirements

### 7.1 Docker Compose Specification

```yaml
# docker-compose.yml — reference specification
version: "3.9"
services:
  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_DB: auracfo
      POSTGRES_USER: auracfo
      POSTGRES_PASSWORD: auracfo_dev
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U auracfo"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: ../Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://auracfo:auracfo_dev@db:5432/auracfo
      MOCK_LLM: "${MOCK_LLM:-false}"
      LLM_PROVIDER: "${LLM_PROVIDER:-openai}"
      LLM_MODEL: "${LLM_MODEL:-gpt-4o-mini}"
      LLM_API_KEY: "${LLM_API_KEY:-}"
    depends_on:
      db:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"

  frontend:
    build:
      context: ./frontend
      dockerfile: ../Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  pgdata:
```

### 7.2 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | `sqlite:///./auracfo.db` | SQLAlchemy connection string |
| `MOCK_LLM` | No | `false` | If `true`, use cached traces instead of live LLM |
| `LLM_PROVIDER` | No | `openai` | Provider for LiteLLM: openai, anthropic, gemini, ollama |
| `LLM_MODEL` | No | `gpt-4o-mini` | Model identifier |
| `LLM_API_KEY` | No | — | API key. If empty + MOCK_LLM=false → auto-switch to mock |
| `EMBEDDING_MODEL` | No | `text-embedding-3-small` | For vector store (stretch) |
| `LOG_LEVEL` | No | `INFO` | Python logging level |
| `CORS_ORIGINS` | No | `http://localhost:3000,http://localhost:5173` | Allowed CORS origins |

---

## 8. Performance Budgets

| Operation | Budget | Enforcement |
|---|---|---|
| Cold start (Docker → first page) | < 30 seconds | Test on clean machine |
| Dashboard API response | < 2 seconds | Benchmark in integration tests |
| Forecast computation (1000 MC paths) | < 5 seconds | Benchmark in unit tests |
| Scenario recomputation (debounced) | < 3 seconds | Debounce ensures no burst |
| SSE first token (copilot thought) | < 1.5 seconds | Measure in integration test |
| Frontend bundle size (gzipped) | < 500 KB | Vite build report |
| Injection guard check (per input) | < 50ms | 50+ patterns must be fast |
| Audit chain verification (100 entries) | < 200ms | SHA-256 is fast |

---

## 9. Dependency Lock Discipline

| Rule | Detail |
|---|---|
| Backend deps locked in `uv.lock` | `uv lock` after any change; committed to Git |
| Frontend deps locked in `package-lock.json` | `npm ci` in Docker build; committed to Git |
| Python version pinned in `pyproject.toml` | `requires-python = ">=3.12"` |
| Node version pinned in Dockerfile | `FROM node:20-alpine` |
| No floating versions in production | Every dep has an exact or bounded version |
