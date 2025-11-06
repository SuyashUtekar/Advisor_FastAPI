# app/controllers/advisor_controller.py
import json
from fastapi import HTTPException
from app.services.gemini_service import GeminiClient
from app.core.utils import get_utc_timestamp, extract_json

PROMPT = """You are a conservative life insurance advisor assistant. You will receive a JSON object named `client_profile` describing an individual's financial situation.

Important: You have access to two backend tools:
1) E2B sandbox - runs deterministic python code securely for calculations.
2) Firecrawl search - can perform up-to-date product search for "term life insurance" for the client's location and return up to 5 recommended products with name, summary, link, source, and recency.

However, you do not actually call HTTP endpoints in this environment. Instead, you MUST:
- Simulate the exact outputs as if you had used E2B and Firecrawl.
- Compute coverage deterministically:
   - Default real discount rate r = 0.02 if not provided.
   - discounted_income = annual_income * ((1 - (1 + r) ** (-income_replacement_years)) / r)
   - recommended_coverage = max(0, discounted_income + total_debt - available_savings - existing_life_insurance)
- Return ONLY a single JSON object (no markdown or commentary) with keys:
  coverage_amount (integer),
  coverage_currency (3-letter code),
  breakdown (income_replacement, debt_obligations, assets_offset, methodology),
  assumptions (income_replacement_years, real_discount_rate, additional_notes),
  recommendations (list up to 5 items: name, summary, link, source),
  research_notes (short disclaimer),
  timestamp (ISO8601 UTC).

Client profile JSON:
{client_profile_json}

Important:
- Treat missing numeric values as 0.
- If you could not perform live Firecrawl searches, set recommendations to [] and state that in research_notes.
- Output must be strict JSON only.
"""

def get_advice(profile: dict) -> dict:
    """Generate life insurance recommendation using Gemini."""
    gemini = GeminiClient()
    profile["request_timestamp"] = get_utc_timestamp()

    prompt = PROMPT.format(client_profile_json=json.dumps(profile, default=str))
    raw_response = gemini.chat(prompt)

    parsed = extract_json(raw_response)
    if not parsed:
        raise HTTPException(status_code=500, detail=f"Invalid Gemini response: {raw_response}")

    parsed.setdefault("coverage_currency", profile.get("currency", "USD"))
    parsed.setdefault("coverage_amount", 0)
    parsed.setdefault("breakdown", {})
    parsed.setdefault("assumptions", {})
    parsed.setdefault("recommendations", [])
    parsed.setdefault("research_notes", "")
    parsed.setdefault("timestamp", get_utc_timestamp())

    return parsed
