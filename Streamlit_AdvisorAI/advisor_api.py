# advisor_api.py
"""
FastAPI version of the Gemini Life Insurance Advisor (prompt-oriented).
- Accepts JSON input (client profile)
- Calls Gemini model
- Returns recommended coverage JSON

Requirements:
  pip install fastapi uvicorn google-generative-ai python-dotenv
Set GOOGLE_API_KEY in .env or environment variables.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    import google.generativeai as genai
    HAS_GENAI = True
except Exception:
    HAS_GENAI = False


# -----------------------------
# Config & Utilities
# -----------------------------
def get_utc_timestamp() -> str:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def extract_json(payload: str) -> Optional[Dict[str, Any]]:
    """Extract JSON block from Gemini response."""
    if not payload:
        return None
    content = payload.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    first = content.find("{")
    last = content.rfind("}")
    if first != -1 and last != -1 and last > first:
        content = content[first:last+1]
    try:
        return json.loads(content)
    except Exception:
        return None


# -----------------------------
# Gemini Client
# -----------------------------
class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        key='AIzaSyDYT3dCXYaf-IuSaomYI0Dms3ua4aXH4Ig'
        if not HAS_GENAI:
            raise RuntimeError("google-generative-ai not installed. pip install google-generative-ai")
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or key
        if not self.api_key:
            raise RuntimeError("Google API key not provided")
        genai.configure(api_key=self.api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(self.model_name)

    def chat(self, prompt: str, temperature: float = 0.0, max_output_tokens: int = 1024) -> str:
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_output_tokens,
                },
            )
            return response.text if hasattr(response, "text") else str(response)
        except Exception as e:
            return json.dumps({
                "error": "gemini_call_failed",
                "detail": str(e),
            })


# -----------------------------
# Gemini Prompt Template
# -----------------------------
PROMPT = """
You are a conservative life insurance advisor assistant. You will receive a JSON object named `client_profile` describing an individual's financial situation.

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


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="AI Life Insurance Advisor API", version="2.0")

# Enable CORS for frontend or Streamlit UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Pydantic Input Schema
# -----------------------------
class ClientProfile(BaseModel):
    age: int
    annual_income: float
    dependents: int
    location: str
    total_debt: float
    available_savings: float
    existing_life_insurance: float
    income_replacement_years: int
    currency: str = "USD"


# -----------------------------
# Routes
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok", "timestamp": get_utc_timestamp()}


@app.post("/advise")
def advise(profile: ClientProfile):
    if not HAS_GENAI:
        raise HTTPException(status_code=500, detail="google-generative-ai not installed")

    gemini = GeminiClient()
    client_profile = profile.dict()
    client_profile["request_timestamp"] = get_utc_timestamp()

    prompt = PROMPT.format(client_profile_json=json.dumps(client_profile, default=str))

    raw_response = gemini.chat(prompt, temperature=0.0, max_output_tokens=1024)
    parsed = extract_json(raw_response)

    if not parsed:
        raise HTTPException(status_code=500, detail=f"Invalid Gemini response: {raw_response}")

    # Ensure required keys
    parsed.setdefault("coverage_currency", client_profile.get("currency", "USD"))
    parsed.setdefault("coverage_amount", 0)
    parsed.setdefault("breakdown", {})
    parsed.setdefault("assumptions", {})
    parsed.setdefault("recommendations", [])
    parsed.setdefault("research_notes", "")
    parsed.setdefault("timestamp", get_utc_timestamp())

    return parsed


# -----------------------------
# Run command:
# -----------------------------
# uvicorn advisor_api:app --reload
