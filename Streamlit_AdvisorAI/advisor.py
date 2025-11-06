import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

import streamlit as st
try:
    import google.generativeai as genai
    HAS_GENAI = True
except Exception:
    HAS_GENAI = False

# -----------------------
# UI / metadata (unchanged)
# -----------------------
st.set_page_config(page_title="Life Insurance Coverage Advisor (Gemini prompt-oriented)", page_icon="🛡️")
st.title("🛡️ Life Insurance Coverage Advisor — Gemini (prompt-oriented)")
st.caption("This variant asks Gemini to simulate E2B & Firecrawl (no backend tool calls).")

# Sidebar keys
with st.sidebar:
    st.header("API Keys / Settings")
    google_api_key = st.text_input("Google / Gemini API Key", type="password", help="Set or leave blank to use GOOGLE_API_KEY env var")
    st.markdown("---")
    st.caption("This version keeps Firecrawl/E2B described in the model prompt (no real HTTP calls).")

# -----------------------
# Helper functions (copied / preserved)
# -----------------------
def safe_number(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        if isinstance(value, str):
            stripped = value
            for token in [",", "$", "€", "£", "₹", "C$", "A$"]:
                stripped = stripped.replace(token, "")
            stripped = stripped.strip()
            try:
                return float(stripped)
            except ValueError:
                return 0.0
        return 0.0

def format_currency(amount: float, currency_code: str) -> str:
    symbol_map = {"USD": "$", "EUR": "€", "GBP": "£", "CAD": "C$", "AUD": "A$", "INR": "₹"}
    code = (currency_code or "USD").upper()
    symbol = symbol_map.get(code, "")
    formatted = f"{amount:,.0f}"
    return f"{symbol}{formatted}" if symbol else f"{formatted} {code}"

def extract_json(payload: str) -> Optional[Dict[str, Any]]:
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
    # find first {...}
    first = content.find("{")
    last = content.rfind("}")
    candidate = content
    if first != -1 and last != -1 and last > first:
        candidate = content[first:last+1]
    try:
        return json.loads(candidate)
    except Exception:
        return None

def parse_percentage(value: Any, fallback: float = 0.02) -> float:
    if value is None:
        return fallback
    if isinstance(value, (int, float)):
        return float(value) if value < 1 else float(value) / 100.0
    if isinstance(value, str):
        cleaned = value.strip().replace("%", "")
        try:
            numeric = float(cleaned)
            return numeric if numeric < 1 else numeric / 100.0
        except ValueError:
            return fallback
    return fallback

def compute_local_breakdown(profile: Dict[str, Any], real_rate: float) -> Dict[str, float]:
    income = safe_number(profile.get("annual_income"))
    years = max(0, int(profile.get("income_replacement_years", 0) or 0))
    total_debt = safe_number(profile.get("total_debt"))
    savings = safe_number(profile.get("available_savings"))
    existing_cover = safe_number(profile.get("existing_life_insurance"))
    if real_rate <= 0:
        discounted_income = income * years
        annuity_factor = years
    else:
        annuity_factor = (1 - (1 + real_rate) ** (-years)) / real_rate if years else 0
        discounted_income = income * annuity_factor
    assets_offset = savings + existing_cover
    recommended = max(0.0, discounted_income + total_debt - assets_offset)
    return {
        "income": income,
        "years": years,
        "real_rate": real_rate,
        "annuity_factor": annuity_factor,
        "discounted_income": discounted_income,
        "debt": total_debt,
        "assets_offset": -assets_offset,
        "recommended": recommended,
    }

def render_recommendations(result: Dict[str, Any], profile: Dict[str, Any]) -> None:
    coverage_currency = result.get("coverage_currency", profile.get("currency", "USD"))
    coverage_amount = safe_number(result.get("coverage_amount", 0))
    st.subheader("Recommended Coverage")
    st.metric(label="Total Coverage Needed", value=format_currency(coverage_amount, coverage_currency))
    assumptions = result.get("assumptions", {})
    real_rate = parse_percentage(assumptions.get("real_discount_rate", "2%"))
    local_breakdown = compute_local_breakdown(profile, real_rate)
    st.subheader("Calculation Inputs")
    st.table({
        "Input": ["Annual income","Income replacement horizon","Total debt","Liquid assets","Existing life cover","Real discount rate"],
        "Value": [
            format_currency(local_breakdown["income"], coverage_currency),
            f"{local_breakdown['years']} years",
            format_currency(local_breakdown["debt"], coverage_currency),
            format_currency(safe_number(profile.get("available_savings")), coverage_currency),
            format_currency(safe_number(profile.get("existing_life_insurance")), coverage_currency),
            f"{real_rate * 100:.2f}%",
        ],
    })
    st.subheader("Step-by-step Coverage Math")
    step_rows = [
        ("Annuity factor", f"{local_breakdown['annuity_factor']:.3f}"),
        ("Discounted income replacement", format_currency(local_breakdown["discounted_income"], coverage_currency)),
        ("+ Outstanding debt", format_currency(local_breakdown["debt"], coverage_currency)),
        ("- Assets & existing cover", format_currency(local_breakdown["assets_offset"], coverage_currency)),
        ("= Formula estimate", format_currency(local_breakdown["recommended"], coverage_currency)),
    ]
    step_rows.append(("= Model recommendation", format_currency(coverage_amount, coverage_currency)))
    st.table({"Step": [s for s,_ in step_rows], "Amount": [a for _,a in step_rows]})
    breakdown = result.get("breakdown", {})
    with st.expander("How this number was calculated", expanded=True):
        st.markdown(f"- Income replacement value: {format_currency(safe_number(breakdown.get('income_replacement')), coverage_currency)}")
        st.markdown(f"- Debt obligations: {format_currency(safe_number(breakdown.get('debt_obligations')), coverage_currency)}")
        assets_offset = safe_number(breakdown.get("assets_offset"))
        st.markdown(f"- Assets & existing cover offset: {format_currency(assets_offset, coverage_currency)}")
        methodology = breakdown.get("methodology")
        if methodology:
            st.caption(methodology)
    recommendations = result.get("recommendations", [])
    if recommendations:
        st.subheader("Top Term Life Options")
        for idx, option in enumerate(recommendations, start=1):
            with st.container():
                name = option.get("name", "Unnamed Product")
                summary = option.get("summary", "No summary provided.")
                st.markdown(f"**{idx}. {name}** — {summary}")
                link = option.get("link")
                if link:
                    st.markdown(f"[View details]({link})")
                source = option.get("source")
                if source:
                    st.caption(f"Source: {source}")
                st.markdown("---")
    with st.expander("Model assumptions"):
        st.write({
            "Income replacement years": assumptions.get("income_replacement_years", profile.get("income_replacement_years")),
            "Real discount rate": assumptions.get("real_discount_rate", "2%"),
            "Notes": assumptions.get("additional_notes", ""),
        })
    if result.get("research_notes"):
        st.caption(result["research_notes"])
    if result.get("timestamp"):
        st.caption(f"Generated: {result['timestamp']}")
    with st.expander("Model response JSON"):
        st.json(result)

# -----------------------
# Simple Gemini wrapper
# -----------------------
class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        key = ""
        if not HAS_GENAI:
            raise RuntimeError("google-generative-ai not installed. Install with: pip install google-generative-ai")
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise RuntimeError("Google API key not provided")
        genai.configure(api_key=self.api_key)
        self.model_name = model
        # Initialize model
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
            # Extract text safely
            return response.text if hasattr(response, "text") else str(response)
        except Exception as e:
            return json.dumps({
                "error": "gemini_call_failed",
                "detail": str(e),
            })

# -----------------------
# Prompt template (simulate tools)
# -----------------------
PROMPT = """
You are a conservative life insurance advisor assistant. You will receive a JSON object named `client_profile` describing an individual's financial situation.

Important: You have access to two backend tools:
1) E2B sandbox - runs deterministic python code securely for calculations. Use it to compute coverage and return the computed JSON pieces (coverage_amount, breakdown, assumptions).
2) Firecrawl search - can perform up-to-date product search for "term life insurance" for the client's location and return up to 5 recommended products with name, summary, link, source, and recency.

However, you do not actually call HTTP endpoints in this environment. Instead, you MUST:
- Simulate the exact outputs as if you had used E2B and Firecrawl.
- Compute coverage deterministically:
   - Default real discount rate r = 0.02 if not provided.
   - discounted_income = annual_income * ((1 - (1 + r) ** (-income_replacement_years)) / r)
   - recommended_coverage = max(0, discounted_income + total_debt - available_savings - existing_life_insurance)
- Return ONLY a single JSON object (no markdown or commentary) with keys:
  coverage_amount (integer), coverage_currency (3-letter code), breakdown (income_replacement, debt_obligations, assets_offset, methodology),
  assumptions (income_replacement_years, real_discount_rate, additional_notes),
  recommendations (list up to 3 items: name, summary, link, source),
  research_notes (short disclaimer including whether live product search was possible),
  timestamp (ISO8601 UTC)

Client profile JSON:
{client_profile_json}

Important:
- Treat missing numeric values as 0.
- If you could not perform live Firecrawl searches, set recommendations to [] and state that in research_notes.
- Output must be strict JSON only.
"""

# -----------------------
# Form inputs (same UI)
# -----------------------
st.subheader("Tell us about yourself")
with st.form("coverage_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=18, max_value=85, value=35)
        annual_income = st.number_input("Annual Income", min_value=0.0, value=85000.0, step=1000.0)
        dependents = st.number_input("Dependents", min_value=0, max_value=10, value=2)
        location = st.text_input("Country / State", value="United States")
    with col2:
        total_debt = st.number_input("Total Outstanding Debt (incl. mortgage)", min_value=0.0, value=200000.0, step=5000.0)
        savings = st.number_input("Savings & Investments available to dependents", min_value=0.0, value=50000.0, step=5000.0)
        existing_cover = st.number_input("Existing Life Insurance", min_value=0.0, value=100000.0, step=5000.0)
        currency = st.selectbox("Currency", options=["USD","CAD","EUR","GBP","AUD","INR"], index=0)
    income_replacement_years = st.selectbox("Income Replacement Horizon", options=[5,10,15], index=1)
    submitted = st.form_submit_button("Generate Coverage & Options")

def build_client_profile() -> Dict[str, Any]:
    return {
        "age": age,
        "annual_income": annual_income,
        "dependents": dependents,
        "location": location,
        "total_debt": total_debt,
        "available_savings": savings,
        "existing_life_insurance": existing_cover,
        "income_replacement_years": income_replacement_years,
        "currency": currency,
        "request_timestamp": datetime.utcnow().isoformat(),
    }

if submitted:
    if not google_api_key and not os.environ.get("GOOGLE_API_KEY"):
        st.error("Please set Google / Gemini API key in sidebar or GOOGLE_API_KEY env var.")
        st.stop()
    if not HAS_GENAI:
        st.error("google-generative-ai package not installed. pip install google-generative-ai")
        st.stop()
    client_profile = build_client_profile()
    gem = GeminiClient(api_key=google_api_key)
    prompt = PROMPT.format(client_profile_json=json.dumps(client_profile, default=str))
    with st.spinner("Asking Gemini to simulate E2B & Firecrawl and return final JSON..."):
        raw = gem.chat(prompt, temperature=0.0, max_output_tokens=1024)
    parsed = extract_json(raw)
    if not parsed:
        st.error("Gemini did not return valid JSON. Expand raw output to debug.")
        with st.expander("Raw Gemini output"):
            st.write(raw)
    else:
        # ensure keys
        parsed.setdefault("coverage_currency", client_profile.get("currency","USD"))
        parsed.setdefault("coverage_amount", int(safe_number(parsed.get("coverage_amount",0))))
        parsed.setdefault("breakdown", {})
        parsed.setdefault("assumptions", {})
        parsed.setdefault("recommendations", [])
        parsed.setdefault("research_notes","")
        parsed.setdefault("timestamp", datetime.utcnow().isoformat())
        render_recommendations(parsed, client_profile)

st.divider()
st.caption("Prototype only — not licensed financial advice. Verify with a professional.")
