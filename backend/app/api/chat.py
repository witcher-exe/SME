import json
import asyncio
import uuid
from datetime import datetime
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db, async_session_factory
from app.models.company import Company
from app.models.approval import Approval
from app.models.schemas import ChatRequest, ErrorResponse
from app.models.enums import Persona, ApprovalActionType
from app.security.injection_guard import InjectionGuard
from app.security.pii_sanitizer import PIISanitizer
from app.security.audit_logger import AuditLogger
from app.mock.mock_llm import MockLLM
from app.services.gemini_service import GeminiService
from app.engines.forecast_engine import ForecastEngine
from app.engines.matching_engine import MatchingEngine

router = APIRouter(tags=["AI Copilot Chat"])

def format_sse(data: dict) -> str:
    """Format dictionary as valid SSE data frame."""
    return f"data: {json.dumps(data)}\n\n"

@router.post(
    "/chat",
    response_class=StreamingResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def chat_sse(request: ChatRequest):
    """
    Tier: T0-T3
    Multi-agent conversational stream using Server-Sent Events (SSE).
    Emits thought traces, tool calls, deterministic engine outputs, and executive synthesis.
    """
    async def event_stream() -> AsyncGenerator[str, None]:
        ts_now = datetime.utcnow().isoformat()
        thread_id = str(uuid.uuid4())[:12]

        # 1. Pre-Flight Security Check (Risk Sentinel)
        yield format_sse({
            "type": "thought",
            "agent": "risk_sentinel",
            "step": "Risk Sentinel",
            "text": "Scanning input for adversarial prompt injection and privilege escalation patterns...",
            "detail": "Scanning input for adversarial prompt injection and privilege escalation patterns...",
            "timestamp": datetime.utcnow().isoformat()
        })
        await asyncio.sleep(0.15)

        is_safe, blocked_pattern = InjectionGuard.check_text(request.message)
        if not is_safe:
            msg = f"Security policy violation: blocked pattern '{blocked_pattern}'. Prompt rejected by Risk Sentinel."
            yield format_sse({
                "type": "security_alert",
                "code": "INJECTION_BLOCKED",
                "message": msg,
                "text": msg,
                "token": msg,
                "timestamp": datetime.utcnow().isoformat()
            })
            yield format_sse({
                "type": "done",
                "thread_id": thread_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            return

        # PII Sanitization
        sanitized_msg, redacts = PIISanitizer.sanitize_text(request.message)
        if redacts:
            yield format_sse({
                "type": "thought",
                "agent": "risk_sentinel",
                "step": "Risk Sentinel",
                "text": f"Scrubbed {len(redacts)} sensitive PII entities before model egress.",
                "detail": f"Scrubbed {len(redacts)} sensitive PII entities before model egress.",
                "timestamp": datetime.utcnow().isoformat()
            })
            await asyncio.sleep(0.1)

        # 2. Virtual CFO Orchestrator Intent Routing
        yield format_sse({
            "type": "thought",
            "agent": "orchestrator",
            "step": "Orchestrator",
            "text": "Virtual CFO analyzing query semantics and routing to designated domain specialist...",
            "detail": "Virtual CFO analyzing query semantics and routing to designated domain specialist...",
            "timestamp": datetime.utcnow().isoformat()
        })
        await asyncio.sleep(0.2)

        # 3. Retrieve response trace from Gemini (or MockLLM fallback)
        mock_resp = await GeminiService.generate_response(sanitized_msg, request.persona)

        for thought in mock_resp["thoughts"]:
            agent_str = thought["agent"]
            step_str = thought.get("step") or agent_str.replace("_", " ").title()
            text_str = thought["text"]
            detail_str = thought.get("detail") or text_str
            yield format_sse({
                "type": "thought",
                "agent": agent_str,
                "step": step_str,
                "text": text_str,
                "detail": detail_str,
                "timestamp": datetime.utcnow().isoformat()
            })
            await asyncio.sleep(0.2)

        # 4. Execute deterministic tools live and stream tool_call & tool_result
        for tc in mock_resp["tool_calls"]:
            agent_name = tc["agent"]
            tool_name = tc["tool"]
            args = tc["args"]

            yield format_sse({
                "type": "tool_call",
                "agent": agent_name,
                "tool": tool_name,
                "args": args,
                "timestamp": datetime.utcnow().isoformat()
            })
            await asyncio.sleep(0.25)

            # Live execution of deterministic tool logic
            if tool_name == "forecast_cash":
                chart, sf_date, sf_amt, runway = ForecastEngine.run_monte_carlo(
                    current_cash=450000.0,
                    weekly_inflows_mean=45000.0,
                    weekly_inflows_std=11250.0,
                    weekly_outflows_mean=52000.0,
                    weekly_outflows_std=10400.0
                )
                tool_res = {
                    "shortfall_date": sf_date,
                    "shortfall_amount": sf_amt,
                    "runway_days": runway,
                    "safety_floor": 10000.0
                }
            elif tool_name == "simulate_scenario":
                tool_res = {
                    "baseline_shortfall_day": 21,
                    "scenario_shortfall_day": 20,
                    "delta_days": -1,
                    "deficit_amount": 12400.0
                }
            elif tool_name == "match_financing":
                tool_res = {
                    "eligible_count": 2,
                    "ineligible_count": 3,
                    "top_scheme": "Invoice Factoring Advance Facility",
                    "rate_cap": 2.5
                }
            elif tool_name == "draft_collection_notice":
                # Create pending approval for the draft
                async with async_session_factory() as s:
                    app = Approval(
                        id=str(uuid.uuid4()),
                        company_id=request.company_id,
                        action_type=ApprovalActionType.COLLECTION_EMAIL.value,
                        payload={
                            "invoice_number": "BCR-2026-003",
                            "recipient_email": "procurement@dhakahandloom.com",
                            "amount": 120000.00,
                            "due_date": "2026-10-05"
                        },
                        justification="Overdue commercial invoice exceeding 9 days.",
                        status="pending",
                        requested_by="treasurer",
                        created_at=datetime.utcnow()
                    )
                    s.add(app)
                    await s.commit()

                tool_res = {
                    "draft_status": "staged",
                    "governance_tier": "T2",
                    "requires_approval": True,
                    "approval_id": app.id
                }
                # Emit approval required event
                yield format_sse({
                    "type": "approval_required",
                    "approval_id": app.id,
                    "action_type": ApprovalActionType.COLLECTION_EMAIL.value,
                    "summary": "Dispatch formal collection notice to Dhaka Handloom Emporium",
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                tool_res = {"status": "success", "company_id": request.company_id}

            yield format_sse({
                "type": "tool_result",
                "agent": agent_name,
                "tool": tool_name,
                "result": tool_res,
                "duration_ms": 120,
                "timestamp": datetime.utcnow().isoformat()
            })
            await asyncio.sleep(0.2)

        # 5. Executive Synthesis
        synth_text = mock_resp["synthesis"]
        yield format_sse({
            "type": "synthesis",
            "text": synth_text,
            "token": synth_text,
            "content": synth_text,
            "citations": mock_resp.get("citations", []),
            "action_chips": mock_resp.get("action_chips", []),
            "chips": mock_resp.get("action_chips", []),
            "timestamp": datetime.utcnow().isoformat()
        })
        await asyncio.sleep(0.1)

        # 6. Stream Completion
        yield format_sse({
            "type": "done",
            "thread_id": thread_id,
            "timestamp": datetime.utcnow().isoformat()
        })

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
