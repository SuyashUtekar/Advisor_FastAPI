# app/core/utils.py
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

def get_utc_timestamp() -> str:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()

def extract_json(payload: str) -> Optional[Dict[str, Any]]:
    """Extract JSON object from a Gemini response."""
    if not payload:
        return None
    content = payload.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        lines = [l for l in lines if not l.startswith("```")]
        content = "\n".join(lines).strip()
    first, last = content.find("{"), content.rfind("}")
    if first != -1 and last != -1 and last > first:
        content = content[first:last+1]
    try:
        return json.loads(content)
    except Exception:
        return None
