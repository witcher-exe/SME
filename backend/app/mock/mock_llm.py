import json
from pathlib import Path
from typing import Dict, Any, List
from app.models.enums import Persona

TRACES_PATH = Path(__file__).parent / "cached_traces.json"

class MockLLM:
    """Provides high-fidelity, deterministic pre-cached reasoning traces for offline judging mode."""

    _cached_data = None

    @classmethod
    def load_traces(cls) -> Dict[str, Any]:
        if cls._cached_data is None:
            if TRACES_PATH.exists():
                with open(TRACES_PATH, "r", encoding="utf-8") as f:
                    cls._cached_data = json.load(f)
            else:
                cls._cached_data = {}
        return cls._cached_data

    @classmethod
    def match_intent(cls, message: str) -> str:
        msg = message.lower()
        if any(w in msg for w in ["yo", "hi", "hello", "whassup", "hey", "sup", "good morning", "good evening", "howdy"]):
            return "greeting"
        elif any(w in msg for w in ["invest", "expansion", "expand", "capex", "growth", "need cash", "need money", "1m", "capital", "acquire", "purchase"]):
            return "investment_capital"
        elif any(w in msg for w in ["scheme", "loan", "financ", "eligible", "why not", "borrow", "fund", "credit", "lending"]):
            return "financing_match"
        elif any(w in msg for w in ["what if", "scenario", "delay", "late", "acme", "shock", "stress", "simulate"]):
            return "scenario_delay"
        elif any(w in msg for w in ["draft", "remind", "collect", "email", "letter", "notice", "overdue", "invoice"]):
            return "draft_collection"
        elif any(w in msg for w in ["runway", "shortfall", "forecast", "cash flow", "burn", "balance", "deficit", "liquidity", "cash"]):
            return "runway_shortfall"
        return "general"

    @classmethod
    def get_response(cls, message: str, persona: Persona = Persona.OWNER) -> Dict[str, Any]:
        traces = cls.load_traces()
        intent = cls.match_intent(message)
        trace = traces.get(intent, traces.get("general", {}))

        synthesis_text = trace.get("cfo_synthesis" if persona == Persona.CFO else "owner_synthesis", "")
        return {
            "intent": intent,
            "thoughts": trace.get("thoughts", []),
            "tool_calls": trace.get("tool_calls", []),
            "synthesis": synthesis_text,
            "citations": trace.get("citations", []),
            "action_chips": trace.get("action_chips", [])
        }
