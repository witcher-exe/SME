import re
from typing import Dict, Any, List, Set, Tuple

class OutputValidator:
    """
    Validates LLM narrative synthesis against deterministic tool outputs.
    Ensures no financial figures are hallucinated (OWASP ASI05 defense).
    """

    @classmethod
    def extract_numbers_from_text(cls, text: str) -> Set[float]:
        """Extracts numerical tokens from natural language text (stripping currency and commas)."""
        # Find potential numbers like $12,400, 8,420, 1.18, 34, 20%
        cleaned = re.sub(r'[,%$\'\"]', '', text)
        tokens = re.findall(r'\b\d+(?:\.\d+)?\b', cleaned)
        numbers = set()
        for t in tokens:
            try:
                val = float(t)
                numbers.add(val)
            except ValueError:
                continue
        return numbers

    @classmethod
    def extract_numbers_from_dict(cls, data: Any) -> Set[float]:
        """Recursively collects all numerical values from tool result dictionaries/lists."""
        numbers = set()
        if isinstance(data, (int, float)):
            numbers.add(float(data))
        elif isinstance(data, dict):
            for v in data.values():
                numbers.update(cls.extract_numbers_from_dict(v))
        elif isinstance(data, list):
            for item in data:
                numbers.update(cls.extract_numbers_from_dict(item))
        return numbers

    @classmethod
    def validate_narrative(
        cls,
        narrative_text: str,
        tool_results: Dict[str, Any],
        tolerance_pct: float = 0.05
    ) -> Tuple[bool, List[float]]:
        """
        Asserts that every significant number in the narrative exists within the tool results.
        Returns (is_valid, list_of_unverified_numbers).
        """
        narrative_nums = cls.extract_numbers_from_text(narrative_text)
        tool_nums = cls.extract_numbers_from_dict(tool_results)

        # Whitelist standard horizon constants, step ordinals, and year numbers (TRD Patch 4B)
        whitelisted_constants = {0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0, 13.0, 14.0, 21.0, 28.0, 30.0, 60.0, 90.0, 1000.0, 2026.0}

        unverified = []
        for n in narrative_nums:
            if n in whitelisted_constants:
                continue
            # Check if n matches any tool number within tolerance
            matched = any(abs(n - tn) / max(tn, 1.0) <= tolerance_pct for tn in tool_nums)
            if not matched:
                unverified.append(n)

        is_valid = len(unverified) == 0
        return is_valid, unverified
