from google import genai
from google.genai import types
from backend.config import GEMINI_API_KEY, MODEL_NAME
from backend.session_store import get_history
import json

client = genai.Client(api_key=GEMINI_API_KEY)

ANALYTICS_PROMPT = """
You are a real estate CRM system. Analyze the conversation history and extract lead data.

Return ONLY a valid JSON object with exactly these fields:
{
  "lead_score": <integer 0-100>,
  "config_interest": "<2BHK|3BHK|both|unknown>",
  "budget_range": "<string or null>",
  "preferred_language": "<English|Hindi|Hinglish|unknown>",
  "visit_booked": <true|false>,
  "visit_date": "<date string or null>",
  "follow_up_required": <true|false>,
  "objections_raised": [<list of strings>],
  "escalated_to_human": <true|false>,
  "interest_level": "<hot|warm|cold>",
  "conversation_summary": "<2-3 sentence summary>"
}

Lead score guide:
- 80-100: Hot lead, ready to buy, visit booked
- 50-79: Warm lead, interested but has objections
- 20-49: Cold lead, just exploring
- 0-19: Uninterested or asked to be removed

Return ONLY the JSON object. No markdown, no explanation, no backticks.
"""


def generate_analytics(session_id: str) -> dict:
    """
    Reads full conversation history for a session.
    Uses Gemini to extract structured lead analytics.
    """
    history = get_history(session_id)

    if not history:
        return {
            "session_id": session_id,
            "lead_score": 0,
            "config_interest": "unknown",
            "budget_range": None,
            "preferred_language": "unknown",
            "visit_booked": False,
            "visit_date": None,
            "follow_up_required": False,
            "objections_raised": [],
            "escalated_to_human": False,
            "interest_level": "cold",
            "conversation_summary": "No conversation found for this session."
        }

    conversation_text = ""
    for msg in history:
        role = "Customer" if msg["role"] == "user" else "Agent"
        text = msg["parts"][0] if msg["parts"] else ""
        conversation_text += f"{role}: {text}\n\n"

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text=f"Analyze this conversation:\n\n{conversation_text}")]
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction=ANALYTICS_PROMPT,
        )
    )

    raw = response.candidates[0].content.parts[0].text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    data = json.loads(raw)
    data["session_id"] = session_id
    return data