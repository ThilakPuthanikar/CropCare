import json
from pathlib import Path
from typing import Iterable, List, Optional

from ..models.scheme import Scheme

_SEEDS_PATH = Path(__file__).resolve().parent.parent.parent / "database" / "seeds" / "schemes.json"


def _load_default_schemes() -> list:
    if _SEEDS_PATH.exists():
        try:
            with open(_SEEDS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


DEFAULT_SCHEMES = _load_default_schemes()


def normalize_text_list(text_value: Optional[Iterable[str] | str]) -> List[str]:
    if not text_value:
        return []

    if isinstance(text_value, str):
        raw_str = text_value.strip()
        if not raw_str:
            return []
        try:
            parsed = json.loads(raw_str)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except (TypeError, ValueError, json.JSONDecodeError):
            pass

        if "\n" in raw_str:
            return [line.strip(" -\t\r") for line in raw_str.splitlines() if line.strip(" -\t\r")]

        return [item.strip() for item in raw_str.split(",") if item.strip()]

    result = []
    for item in text_value:
        if item is not None:
            cleaned = str(item).strip()
            if cleaned:
                result.append(cleaned)
    return result


def serialize_text_list(items: Optional[Iterable[str] | str]) -> Optional[str]:
    normalized_items = normalize_text_list(items)
    if not normalized_items:
        return None
    return json.dumps(normalized_items)


def scheme_to_payload(scheme: Scheme) -> dict:
    return {
        "id": scheme.id,
        "title": scheme.title,
        "description": scheme.description or "Scheme details are available from the official source.",
        "type": scheme.type or "national",
        "beneficiary": scheme.beneficiary or "general",
        "benefits": scheme.benefits or "Refer to the official scheme guidance.",
        "eligibility": scheme.eligibility or "Check the official eligibility criteria before applying.",
        "documents_required": normalize_text_list(scheme.documents_required),
        "steps_to_apply": normalize_text_list(scheme.steps_to_apply),
        "duration": scheme.duration or "Refer to official notification",
        "official_link": scheme.official_link or "#",
        "icon": scheme.icon or "fas fa-hand-holding-heart",
        "state": scheme.state,
        "district": scheme.district,
        "is_active": bool(scheme.is_active),
        "created_at": scheme.created_at,
        "updated_at": scheme.updated_at,
    }
