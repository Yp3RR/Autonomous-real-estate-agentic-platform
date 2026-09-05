from google import genai
from google.genai import types
from backend.config import GEMINI_API_KEY, MODEL_NAME
from backend.session_store import get_history, add_message
from backend.tools import TOOL_DEFINITIONS, execute_tool
from logger import get_logger, log_tool_fired
logger = get_logger()
import pathlib

# Configure Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Load system prompt from file
PROMPT_PATH = pathlib.Path(__file__).parent.parent / "prompts" / "1st_system_prompt.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")

# Conversation end signals
END_PHRASES = [
    "have a good day", "goodbye", "take care", "thank you for your time",
    "we will not contact you", "you've been removed", "talk soon",
    "have a great day", "all the best"
]


def _conversation_ended(text: str) -> bool:
    """Check if agent response signals end of conversation."""
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in END_PHRASES)


def _build_tools() -> list:
    """Convert our tool definitions to new SDK format."""
    declarations = [
        types.FunctionDeclaration(
            name=tool["name"],
            description=tool["description"],
            parameters=tool["parameters"]
        )
        for tool in TOOL_DEFINITIONS
    ]
    return [types.Tool(function_declarations=declarations)]


def _history_to_contents(history: list) -> list:
    """Convert session history to new SDK Content format."""
    contents = []
    for msg in history:
        role = msg["role"]  # "user" or "model"
        text = msg["parts"][0] if msg["parts"] else ""
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part(text=text)]
            )
        )
    return contents


def run_agent(session_id: str, user_message: str) -> dict:
    """
    Main agentic loop.

    1. Load session history
    2. Send to Gemini with system prompt + tools
    3. If Gemini returns a tool call:
       a. Execute tool via tools.py
       b. Send result back to Gemini
       c. Repeat until Gemini returns a text response
    4. Save final response to history
    5. Return response + whether conversation ended
    """

    # Step 1: Build conversation history
    history = get_history(session_id)
    contents = _history_to_contents(history)

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part(text=user_message)]
        )
    )

    # Step 2: Agentic loop
    max_iterations = 10
    iteration = 0
    response_text = ""

    while iteration < max_iterations:
        iteration += 1

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=_build_tools(),
                tool_config=types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(
                        mode="AUTO"
                    )
                )
            )
        )

        candidate = response.candidates[0]
        parts = candidate.content.parts

        tool_call_parts = [p for p in parts if p.function_call is not None]

        if tool_call_parts:
            contents.append(
                types.Content(
                    role="model",
                    parts=parts
                )
            )

            tool_response_parts = []
            for part in tool_call_parts:
                tool_name = part.function_call.name
                tool_args = dict(part.function_call.args)

                print(f"[Agent] Tool call: {tool_name}({tool_args})")

                result = execute_tool(tool_name, tool_args)
                log_tool_fired(logger, session_id, tool_name, result)

                tool_response_parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=tool_name,
                            response=result
                        )
                    )
                )

            contents.append(
                types.Content(
                    role="user",
                    parts=tool_response_parts
                )
            )
            continue

        # No tool calls — extract text response
        text_parts = [p.text for p in parts if p.text]
        if text_parts:
            response_text = " ".join(text_parts).strip()
            break

        response_text = "I'm sorry, I ran into an issue. Could you please repeat that?"
        break

    if not response_text:
        response_text = "I'm sorry, something went wrong. Please try again."

    # Step 3: Save to session history
    add_message(session_id, "user", user_message)
    add_message(session_id, "model", response_text)

    # Step 4: Return
    return {
        "response": response_text,
        "conversation_ended": _conversation_ended(response_text)
    }