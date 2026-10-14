import json
from pathlib import Path
from typing import List, Optional
from app.models.schemas import SchemeDefinition

SCHEMES_DIR = Path(__file__).parent / "schemes"

class SchemeCatalog:
    """Loads, validates, and serves dated, citable financing scheme definitions."""

    @classmethod
    def load_all(cls) -> List[SchemeDefinition]:
        schemes: List[SchemeDefinition] = []
        if not SCHEMES_DIR.exists():
            return schemes

        for file_path in SCHEMES_DIR.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    schemes.append(SchemeDefinition.model_validate(data))
            except Exception as e:
                print(f"[SchemeCatalog] Failed to load {file_path.name}: {e}")

        # Sort by rate ascending for optimal recommendation ordering
        schemes.sort(key=lambda s: s.rate_cap_pct)
        return schemes

    @classmethod
    def get_by_id(cls, scheme_id: str) -> Optional[SchemeDefinition]:
        for scheme in cls.load_all():
            if scheme.id == scheme_id:
                return scheme
        return None
