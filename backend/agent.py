import google.generativeai as genai
from backend.config import GEMINI_API_KEY, MODEL_NAME
from backend.session_store import get_history, add_message
from backend.tools import TOOL_DEFINITIONS, execute_tool
import pathlib
import json

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Load system prompt from file
PROMPT_PATH = pathlib.Path(__file__).parent.parent / "prompts" / "v1_system_prompt.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")

# Conversation end signals
END_PHRASES = [
    "have a good day", "goodbye", "take care", "thank you for your time",
    "we will not contact you", "you've been removed", "talk soon",
    "have a great day", "all the best"
]


def _conversation_ended(text: str) -> bool:
    """Check if agent's response signals end of conversation."""
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in END_PHRASES)


def _build_tool_config() -> list:
    """Convert our tool definitions to Gemini's expected format."""
    return [{
        "function_declarations": TOOL_DEFINITIONS
    }]


def run_agent(session_id: str, user_message: str) -> dict:
    """
    Main agentic loop.

    1. Load session history
    2. Add user message to history
    3. Send to Gemini with system prompt + tools
    4. If Gemini returns a tool call:
       a. Execute the tool via tools.py
       b. Send result back to Gemini
       c. Repeat until Gemini returns a text response
    5. Save final response to history
    6. Return response + whether conversation ended
    """

    # Step 1: Load history and add user message
    history = get_history(session_id)
    add_message(session_id, "user", user_message)

    # Step 2: Build updated history for this request
    current_history = get_history(session_id)

    # Step 3: Initialise Gemini model with system prompt and tools
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT,
        tools=_build_tool_config()
    )

    chat = model.start_chat(history=current_history[:-1])

    # Step 4: Agentic loop — keep going until we get a text response
    max_iterations = 5
    iteration = 0
    response_text = ""

    current_message = user_message

    while iteration < max_iterations:
        iteration += 1

        response = chat.send_message(current_message)
        candidate = response.candidates[0]
        parts = candidate.content.parts

        tool_calls = [p for p in parts if hasattr(p, "function_call") and p.function_call.name]

        if tool_calls:
            tool_results = []

            for part in tool_calls:
                tool_name = part.function_call.name
                tool_args = dict(part.function_call.args)

                print(f"[Agent] Tool call: {tool_name}({tool_args})")

                result = execute_tool(tool_name, tool_args)

                tool_results.append({
                    "function_response": {
                        "name": tool_name,
                        "response": result
                    }
                })

            import google.generativeai.types as genai_types
            tool_response_parts = [
                genai_types.Part(
                    function_response=genai_types.FunctionResponse(
                        name=tr["function_response"]["name"],
                        response=tr["function_response"]["response"]
                    )
                )
                for tr in tool_results
            ]

            response = chat.send_message(tool_response_parts)
            candidate = response.candidates[0]
            parts = candidate.content.parts

        # Extract text response
        text_parts = [p.text for p in parts if hasattr(p, "text") and p.text]

        if text_parts:
            response_text = " ".join(text_parts).strip()
            break

        if not tool_calls:
            response_text = "I'm sorry, I ran into an issue. Could you please repeat that?"
            break

    if not response_text:
        response_text = "I'm sorry, something went wrong on my end. Please try again."

    # Step 5: Save agent response to history
    add_message(session_id, "model", response_text)

    # Step 6: Return response
    return {
        "response": response_text,
        "conversation_ended": _conversation_ended(response_text)
    }