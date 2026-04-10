"""Gemini-powered sentiment analyzer for editorial headlines."""

import json
import os
import re

from dotenv import load_dotenv
try:
    import google.generativeai as genai
except ImportError:
    genai = None

load_dotenv()
if genai is not None:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
    MODEL = genai.GenerativeModel("gemini-1.5-flash")
else:
    MODEL = None


def _default_neutral(reason="Analysis unavailable"):
    """Return the required neutral fallback payload."""
    return {"sentiment": "neutral", "score": 0, "reason": reason}


def _clean_model_text(raw_text):
    """Strip markdown wrappers and isolate a JSON object from model output."""
    cleaned = (raw_text or "").strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    json_match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    return json_match.group(0) if json_match else cleaned


def analyze_sentiment(headline):
    """Analyze a single headline and return sentiment, score, and reason.

    Args:
        headline: News headline string.

    Returns:
        Dictionary with keys: sentiment, score, reason.
    """
    if MODEL is None:
        return _default_neutral("google-generativeai not installed")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_key_here":
        return _default_neutral("GEMINI_API_KEY not configured")

    try:
        prompt = (
            "Analyze the sentiment of this news headline and return ONLY a raw JSON object "
            "with no markdown, no backticks, no explanation. JSON must have: sentiment "
            "(positive/neutral/negative), score (integer from -100 to 100), reason (one "
            f"sentence max). Headline: {headline}"
        )

        response = MODEL.generate_content(prompt)
        response_text = _clean_model_text(getattr(response, "text", ""))
        parsed = json.loads(response_text)

        sentiment = str(parsed.get("sentiment", "neutral")).lower().strip()
        if sentiment not in {"positive", "neutral", "negative"}:
            sentiment = "neutral"

        score = int(float(parsed.get("score", 0)))
        score = max(-100, min(100, score))

        reason = str(parsed.get("reason", "No reason provided")).strip()
        if not reason:
            reason = "No reason provided"

        return {"sentiment": sentiment, "score": score, "reason": reason[:180]}
    except Exception:
        return _default_neutral()
