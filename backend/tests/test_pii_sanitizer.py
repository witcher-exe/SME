import pytest
from app.security.pii_sanitizer import PIISanitizer
from app.models.enums import PIICategory

def test_sanitize_phone_numbers():
    text = "Payment received from customer 01711002233 via bKash."
    sanitized, tokens = PIISanitizer.sanitize_text(text)
    assert "01711002233" not in sanitized
    assert "HMAC_PHONE_" in sanitized
    assert len(tokens) == 1
    assert tokens[0]["category"] == PIICategory.PHONE_NUMBER.value

def test_sanitize_tax_ids():
    text = "Supplier invoice from Dhaka Crafts Ref: TIN-9821-4412."
    sanitized, tokens = PIISanitizer.sanitize_text(text)
    assert "TIN-9821-4412" not in sanitized
    assert "HMAC_TIN_" in sanitized
    assert len(tokens) == 1
    assert tokens[0]["category"] == PIICategory.TAX_ID.value

def test_deterministic_tokenization():
    """Identical raw text produces identical HMAC tokens."""
    token1 = PIISanitizer.generate_token("01819223344", PIICategory.PHONE_NUMBER)
    token2 = PIISanitizer.generate_token("01819223344", PIICategory.PHONE_NUMBER)
    assert token1 == token2
    assert token1.startswith("HMAC_PHONE_")
