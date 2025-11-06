# app/services/gemini_service.py
import json
import google.generativeai as genai
from typing import Optional
from app.core.config import settings

class GeminiClient:
    """Handles Gemini API communication."""

    def __init__(self, api_key: Optional[str] = None, model: str = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        if not self.api_key:
            raise RuntimeError("Google API key not found. Set GOOGLE_API_KEY in environment.")
        self.model_name = model or settings.GEMINI_MODEL
        genai.configure(api_key=self.api_key)
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
