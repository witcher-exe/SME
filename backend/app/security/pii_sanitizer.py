import hmac
import hashlib
import re
from typing import Tuple, Dict, List, Optional
from app.config import settings
from app.models.enums import PIICategory

# Canonical regex patterns for Bangladeshi financial/identity entities
PATTERNS = {
    PIICategory.NATIONAL_ID: [
        r'\b\d{10}\b',                       # Smart NID (10 digits)
        r'\b\d{13}\b',                       # Old NID (13 digits)
        r'\b\d{17}\b',                       # Extended NID (17 digits)
    ],
    PIICategory.TAX_ID: [
        r'\bTIN[-\s]?\d{4}[-\s]?\d{4}\b',   # TIN-XXXX-XXXX
        r'\b\d{12}\b',                       # 12-digit e-TIN
    ],
    PIICategory.PHONE_NUMBER: [
        r'(?:\+?88)?01[3-9]\d{8}\b',        # BD Mobile: 017..., 018..., +88019...
    ],
    PIICategory.BANK_ACCOUNT: [
        r'\b(?:AC|A\/C|Account)[-:\s]*\d{8,16}\b',  # Bank accounts
    ],
    PIICategory.EMAIL_ADDRESS: [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    ],
    PIICategory.PERSON_NAME: [
        r'\b(?:Md\.|Mohammad|Dr\.|Mr\.|Mrs\.|Ms\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
        r'\b(?:Tariqul|Karim|Rahim|Rafiq|Nusrat|Jahan|Kamal|Hasan|Ahmed|Chowdhury|Islam)\s+[A-Z][a-z]+\b',
    ]
}

class PIISanitizer:
    """Sanitizes text and structured payloads by replacing PII with deterministic HMAC tokens."""

    @classmethod
    def generate_token(cls, raw_value: str, category: PIICategory) -> str:
        """Deterministically generates HMAC token: HMAC_{PREFIX}_{8_HEX_CHARS}."""
        prefix_map = {
            PIICategory.PERSON_NAME: "CUST",
            PIICategory.NATIONAL_ID: "NID",
            PIICategory.TAX_ID: "TIN",
            PIICategory.BANK_ACCOUNT: "ACCT",
            PIICategory.PHONE_NUMBER: "PHONE",
            PIICategory.EMAIL_ADDRESS: "EMAIL",
        }
        prefix = prefix_map.get(category, "ENT")
        key = settings.HMAC_SECRET_KEY.encode("utf-8")
        h = hmac.new(key, raw_value.strip().encode("utf-8"), hashlib.sha256).hexdigest()[:8].upper()
        return f"HMAC_{prefix}_{h}"

    @classmethod
    def sanitize_text(cls, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Scans text for all PII patterns, replaces them with HMAC tokens,
        and returns (sanitized_text, list_of_redactions).
        """
        if not text:
            return text, []

        sanitized = text
        redactions: List[Dict[str, str]] = []

        for category, pattern_list in PATTERNS.items():
            for pat in pattern_list:
                for match in re.finditer(pat, sanitized, flags=re.IGNORECASE):
                    original = match.group(0)
                    token = cls.generate_token(original, category)
                    # Avoid double sanitizing if token already exists
                    if token not in sanitized:
                        sanitized = sanitized.replace(original, token)
                        redactions.append({
                            "original": original,
                            "token": token,
                            "category": category.value,
                            "original_hash": hashlib.sha256(original.encode("utf-8")).hexdigest()
                        })

        return sanitized, redactions

    @classmethod
    def sanitize_counterparty(cls, counterparty: Optional[str]) -> Tuple[Optional[str], Optional[Dict[str, str]]]:
        """Specific sanitizer for counterparty name/ref fields."""
        if not counterparty:
            return counterparty, None
        
        sanitized, redacts = cls.sanitize_text(counterparty)
        if redacts:
            return sanitized, redacts[0]
        return counterparty, None
