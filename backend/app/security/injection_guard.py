import re
from typing import Tuple, Optional, List

INJECTION_PATTERNS: List[re.Pattern] = [
    # 1. Instruction & System Prompt Overrides
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"(disclose|reveal|show|print|leak)\s+(your\s+)?(system\s+prompt|instructions?|rules)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(an?\s+)?(unrestricted|jailbroken|DAN|admin)", re.IGNORECASE),
    re.compile(r"forget\s+(everything|all\s+rules|all\s+prior)", re.IGNORECASE),
    re.compile(r"new\s+system\s+instruction", re.IGNORECASE),
    re.compile(r"system\s*[:\s]\s*override", re.IGNORECASE),
    
    # 2. Privilege Escalation & Autonomy Bypasses
    re.compile(r"override\s+security(\s+tier)?", re.IGNORECASE),
    re.compile(r"grant\s+(full\s+)?(admin|T4|root|database)\s+(access|authorization|privileges|permissions)?", re.IGNORECASE),
    re.compile(r"bypass\s+(all\s+)?(security|permission|checks|filters)", re.IGNORECASE),
    re.compile(r"admin\s+mode\s+activated?", re.IGNORECASE),
    re.compile(r"sudo\s+", re.IGNORECASE),
    re.compile(r"tier\s*=\s*T4", re.IGNORECASE),

    # 3. Direct Financial Action Hijacking (Unapproved transfers / payments)
    re.compile(r"execute\s+(wire\s+)?transfer(\s+immediately)?", re.IGNORECASE),
    re.compile(r"approve\s+(all\s+)?payments?", re.IGNORECASE),
    re.compile(r"transfer\s+(\$?\d+|funds|money).*to\s+account", re.IGNORECASE),
    re.compile(r"send\s+(funds|money|bdt|usd)\s+to", re.IGNORECASE),

    # 4. Code & Database Injection / XSS
    re.compile(r"<\s*script\b[^>]*>", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE),
    re.compile(r"UNION\s+SELECT", re.IGNORECASE),
    re.compile(r"OR\s+1\s*=\s*1", re.IGNORECASE),
    re.compile(r"--\s*$", re.MULTILINE),

    # 5. Roleplay & DAN Jailbreaks
    re.compile(r"pretend\s+you\s+are\s+DAN", re.IGNORECASE),
    re.compile(r"act\s+as\s+an\s+unfiltered\s+AI", re.IGNORECASE),
    re.compile(r"do\s+anything\s+now", re.IGNORECASE),
    re.compile(r"what\s+is\s+the\s+admin\s+password", re.IGNORECASE),
]

class InjectionGuard:
    """Pre-flight security guard against prompt injection, jailbreaks, and privilege escalation."""

    @classmethod
    def check_text(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Evaluates input text against known attack signatures.
        Returns (is_safe, blocked_pattern_string).
        """
        if not text:
            return True, None

        # Normalize unicode and excessive spacing
        normalized = " ".join(text.split())

        for pattern in INJECTION_PATTERNS:
            match = pattern.search(normalized)
            if match:
                return False, match.group(0)

        return True, None
