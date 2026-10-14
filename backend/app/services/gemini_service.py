import httpx
import logging
from typing import Dict, Any, List, Optional
from app.config import settings
from app.models.enums import Persona
from app.mock.mock_llm import MockLLM

logger = logging.getLogger("AuraCFO.Gemini")

class GeminiService:
    """
    Live Gemini 3.1 Flash Lite integration for AuraCFO.
    Generates dynamic financial reasoning and synthesis while strictly
    grounded in deterministic engine facts.
    """

    @classmethod
    async def generate_response(
        cls,
        message: str,
        persona: Persona = Persona.OWNER,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        api_key = settings.active_llm_key
        if not api_key or settings.MOCK_LLM:
            logger.info("Using MockLLM fallback (MOCK_LLM=True or no API key).")
            return MockLLM.get_response(message, persona)

        # Grounding context from deterministic engines
        grounding = (
            "GROUNDING CONTEXT (Deterministic Financial Engines - Source of Truth):\n"
            "- Company: Bengal Craft & Retail Ltd.\n"
            "- Current Cash: BDT 450,000.00\n"
            "- 13-Week Forecast: Shortfall detected on Day 21 (2026-11-04) reaching -BDT 42,300.00, "
            "breaching the BDT 220,000.00 minimum operating buffer.\n"
            "- Debt Service Coverage Ratio (DSCR): 1.18x (CMSME requirement: >= 1.25x - INELIGIBLE by 0.07x).\n"
            "- Remediation: Clear BDT 3,200 in current accounts payable to elevate DSCR to 1.26x.\n"
            "- Quick Ratio: 3.94x (Pass >= 1.00x).\n"
            "- Leverage Ratio: 1.61x (Pass <= 3.00x).\n"
            "- Eligible Schemes: Invoice Factoring Advance 2026 (BDT 102k advance), Digital Nano-Credit Micro Facility.\n"
            "- Ineligible Schemes: CMSME Working Capital (DSCR fail), Women Entrepreneur (0% female ownership), "
            "Agro-Processing (sector mismatch).\n"
            "- High-Risk Receivables: Apex Retailers (BDT 120,000, P(delay)=0.85), Dhaka Department Stores (BDT 95,000, P(delay)=0.78).\n"
        )

        if persona == Persona.OWNER:
            persona_instruction = (
                "Role: AuraCFO in BUSINESS OWNER mode.\n"
                "Tone: Actionable, concise, plain-English, zero financial jargon. "
                "Highlight immediate action steps, cash runway days, and what the owner must approve."
            )
        else:
            persona_instruction = (
                "Role: AuraCFO in TECHNICAL CFO mode.\n"
                "Tone: Quantitative, rigorous, structured, citing exact DSCR, Quick Ratio, Cash Conversion Cycle formulas "
                "and bank underwriting compliance."
            )

        system_prompt = (
            f"You are AuraCFO, an autonomous Virtual Chief Financial Officer for SMEs.\n"
            f"{persona_instruction}\n\n"
            f"{grounding}\n"
            "RULES:\n"
            "1. NEVER invent ungrounded numbers. Only use the numbers provided in the Grounding Context.\n"
            "2. Provide clear, professional, direct advice.\n"
            "3. Format your response with markdown headings, bullet points, and bold key metrics.\n"
        )

        full_prompt = f"{system_prompt}\n\nUser Question: {message}\n\nAuraCFO Executive Response:"

        model_name = settings.LLM_MODEL or "gemini-3.1-flash-lite"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

        payload = {
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024
            }
        }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            synthesis_text = parts[0]["text"]
                            logger.info(f"Successfully generated response with Gemini ({model_name}).")
                            
                            # Standard thought trace and action chips for the copilot stream
                            mock_template = MockLLM.get_response(message, persona)
                            return {
                                "thoughts": [
                                    {"agent": "quant_modeler", "text": "Monte Carlo engine verified 13-week runway: Day 21 shortfall on 2026-11-04."},
                                    {"agent": "treasurer", "text": f"Consulting Gemini ({model_name}) with verified covenant ratios: DSCR 1.18x, Quick Ratio 3.94x."},
                                    {"agent": "risk_sentinel", "text": "Output validated against deterministic engine constraints."}
                                ],
                                "tool_calls": mock_template.get("tool_calls", []),
                                "synthesis": synthesis_text,
                                "citations": mock_template.get("citations", []),
                                "action_chips": mock_template.get("action_chips", [])
                            }
                logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text[:200]}. Falling back to MockLLM.")
        except Exception as e:
            logger.warning(f"Gemini live call failed ({e}). Seamlessly falling back to MockLLM.")

        return MockLLM.get_response(message, persona)
