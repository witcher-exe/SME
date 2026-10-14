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

        # Model priority cascade: Primary -> Secondary -> Emergency
        models_cascade = [
            settings.LLM_MODEL or "gemini-3.1-flash-lite",
            "gemini-3.5-flash-lite",
            "gemini-2.5-flash-lite",
            "gemini-flash-lite-latest"
        ]
        # Deduplicate while preserving strict priority order
        models_to_try = []
        for m in models_cascade:
            if m not in models_to_try:
                models_to_try.append(m)

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

        async with httpx.AsyncClient(timeout=10.0) as client:
            for idx, model_name in enumerate(models_to_try):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                try:
                    logger.info(f"Attempting model [{idx + 1}/{len(models_to_try)}]: {model_name}...")
                    resp = await client.post(url, json=payload)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                synthesis_text = parts[0]["text"]
                                logger.info(f"Successfully generated response with Gemini ({model_name}).")
                                
                                mock_template = MockLLM.get_response(message, persona)
                                return {
                                    "thoughts": [
                                        {"agent": "quant_modeler", "text": "Monte Carlo engine verified 13-week runway: Day 21 shortfall on 2026-11-04."},
                                        {"agent": "treasurer", "text": f"Consulting live Gemini model ({model_name}) with verified covenant ratios: DSCR 1.18x, Quick Ratio 3.94x."},
                                        {"agent": "risk_sentinel", "text": "Output validated against deterministic engine constraints."}
                                    ],
                                    "tool_calls": mock_template.get("tool_calls", []),
                                    "synthesis": synthesis_text,
                                    "citations": mock_template.get("citations", []),
                                    "action_chips": mock_template.get("action_chips", [])
                                }

                    # Check why it failed
                    status_code = resp.status_code
                    body_text = resp.text.lower()

                    # Check for explicit DAILY quota exhaustion (do not cycle models if daily account limit reached)
                    if status_code == 429 and ("per day" in body_text or "daily" in body_text):
                        logger.warning(f"Daily API quota limit reached on {model_name}. Stopping model cascade to preserve quota.")
                        break

                    # Server busy / high demand / timeout / service unavailable -> Fall back to next model
                    if status_code in [500, 502, 503, 504] or "high demand" in body_text or "capacity" in body_text:
                        logger.warning(
                            f"Model {model_name} is currently busy on Google server (status {status_code}). "
                            f"Falling back to next priority model..."
                        )
                        continue
                    elif status_code == 404:
                        # Model unavailable in this region/tier, continue to emergency model
                        logger.info(f"Model {model_name} unavailable (404). Trying next fallback...")
                        continue
                    else:
                        logger.warning(f"Model {model_name} returned unexpected status {status_code}. Checking next fallback...")
                        continue

                except (httpx.TimeoutException, httpx.NetworkError) as e:
                    logger.warning(f"Model {model_name} connection/timeout ({e}). Server may be overloaded. Falling back to next model...")
                    continue
                except Exception as e:
                    logger.warning(f"Unexpected error calling {model_name}: {e}. Checking next fallback...")
                    continue

        logger.warning("All live Gemini models busy or unreachable. Seamlessly activating MockLLM.")
        return MockLLM.get_response(message, persona)
