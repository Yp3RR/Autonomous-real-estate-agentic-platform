# **Northstar AI Agent**

An agentic AI sales assistant for Northstar One, a residential project in Sector 79, Gurugram. 
Built with FastAPI and Google Gemini — the agent autonomously qualifies leads, answers project queries, 
books site visits via real tool calls, and generates structured lead analytics after every conversation.

### Status: *Complete — deployed and containerized.*
**Live:** (https://autonomous-real-estate-agentic-platform.onrender.com/)
 ---

## What Makes This Agentic

Most real estate chatbots are scripted — if user says "book" → show booking form. This agent is different.

When a customer asks to book a site visit, Gemini decides to:

1. Call check_availability() to verify slots exist
2. Collect the customer's name and phone naturally through conversation
3. Call book_site_visit() with the collected details
4. If booking fails → call escalate_to_human() and explain the situation
5. Call log_lead() before ending with all gathered intelligence

None of that sequence is hardcoded. The LLM decides what to call, when, and in what order — based on the conversation context. That's the agentic part.

---

## Features
### Multilingual: 
natural conversation in English, Hindi, and Hinglish
### Lead qualification: 
understands budget, configuration preference, timeline, and intent
### Agentic tool use: 
checks availability, books visits, escalates, logs leads autonomously
### Objection handling: 
price concerns, "call me later", "stop contacting me" all handled gracefully
### Booking failure handling: 
15% simulated failure rate with proper fallback behaviour
### Post-conversation analytics: 
lead score (0–100), interest level, objections raised, conversation summary
### Session memory: 
full conversation context maintained across multiple turns
### No hallucination: 
agent is constrained to only state facts provided in the system prompt
### Structured logging:
every request, response, tool call, and error logged as JSON with session ID and duration
### Guardrails:
input and output validation to prevent prompt injection and off-topic responses
### Evaluation framework:
per-turn response quality scoring to measure agent reliability
### Dockerized:
fully containerized with Dockerfile for consistent local and cloud deployment

---

## Tech Stack

| Layer | Tool                    |
|---|-------------------------|
| LLM | Google Gemini 3.6 Flash |
| Backend | FastAPI (Python)        |
| Session Memory | SQLite (persistent per session) |
| Data Validation | Pydantic v2             |
| Logging | Structured JSON logging (file + stdout) |
| Frontend | HTML + CSS + Vanilla JS |
| Deploy | Render (backend + frontend) |
| Containerization | Docker |
---
## Project Structure

```
northstar-ai-agent/
│
├── backend/
│   ├── main.py              # FastAPI app — all routes
│   ├── agent.py             # Agentic loop — Gemini + tool call handling
│   ├── tools.py             # Tool definitions + simulated implementations
│   ├── session_store.py     # In-memory conversation history per session
│   ├── analytics.py         # Post-conversation lead analytics generator
│   ├── models.py            # Pydantic request/response schemas
│   └── config.py            # Environment variable loader
│
├── prompts/
│   └── v1_system_prompt.md  # System prompt — agent identity, facts, conversation flow
│
├── frontend/
│   ├── index.html           # Chat UI
│   ├── style.css            # Styling
│   └── app.js               # API calls, message rendering, analytics modal
│
├── tests/
│   └── TEST_CASES.md        # Conversation scenarios with expected vs actual output
│
├── logger.py            # Structured JSON logging
├── evals.py             # Response quality evaluation
├── Dockerfile           # Container config
├── .dockerignore
├── logs/
│   └── northstar.log    # Structured log output
├── render.yaml              # Render deployment config
├── requirements.txt
├── .env.example
└── README.md
```
## How It Works

```
User message
      ↓
FastAPI /chat endpoint
      ↓
agent.py — loads session history + system prompt
      ↓
Gemini API (with tool definitions)
      ↓ (if tool call returned)
tools.py — executes tool, returns result to Gemini
      ↓ (loop until text response)
Final response saved to session store
      ↓
Response returned to frontend

── conversation ends ──

FastAPI /analytics endpoint
      ↓
analytics.py — reads full history, sends to Gemini
      ↓
Structured lead card (JSON) returned to frontend
```

---
## Agent Capabilities (System Prompt Coverage)

| Scenario | Handled |
|---|---|
| Natural greeting and qualification | ✅ |
| English / Hindi / Hinglish | ✅ |
| Price objection | ✅ |
| "I'm just exploring" | ✅ |
| "Call me later" | ✅ |
| "Stop contacting me" | ✅ |
| Unknown questions (no hallucination) | ✅ |
| Site visit booking | ✅ |
| Booking failure fallback | ✅ |
| Human escalation | ✅ |
| Lead logging at conversation end | ✅ |

---
## How to Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/Yp3RR/northstar-ai-agent.git
cd northstar-ai-agent
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```bash
cp .env.example .env
# Add your Gemini API key to .env
# Get a free key at: https://aistudio.google.com/app/apikey
```

**5. Run the server**
```bash
python -m uvicorn backend.main:app --reload
```

**6. Open in browser**
```
http://127.0.0.1:8000
```

Or test the API directly at `http://127.0.0.1:8000/docs`

---
## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat` | Send a message, get agent response |
| POST | `/analytics` | Generate lead summary for a session |
| DELETE | `/session/{id}` | Clear conversation history |
| GET | `/health` | Health check |

**Sample `/chat` request:**
```json
{
  "session_id": "user-abc123",
  "message": "Hi, I'm looking for a 3BHK in Gurugram"
}
```

**Sample `/chat` response:**
```json     
{
  "session_id": "user-abc123",
  "response": "Hi! I'm Dhruv from Northstar Homes...",
  "conversation_ended": false
}
```

---
## Key Assumptions

- Session memory is persisted to SQLite — restarting the server on free-tier hosting clears the DB (use hosted DB like Supabase for production)
- Booking and availability are simulated — no real calendar or CRM integration
- The agent never reveals it is an AI unless directly and sincerely asked
- All project facts (pricing, area, amenities) are sourced only from the system prompt — no external data fetch

---
## Known Limitations

- SQLite DB is ephemeral on Render free tier — resets on every redeploy (one-line fix: swap DB_PATH to a hosted Postgres/Supabase connection string)
- Gemini free tier rate limits cause occasional response failures — retry logic implemented, paid tier recommended for production
- No rate limiting on API endpoints (planned)
- No authentication on session endpoints — any client can clear any session by ID
- Analytics generation makes an additional Gemini API call — adds ~2s latency

---

## AI Tools Used

- **Google Gemini 3.6 Flash** — LLM powering the agent and analytics pipeline
- **Claude (Anthropic)** — used during development for code assistance, architecture decisions, and prompt engineering iteration

---

## Author

**Yash Patil**
B.E. Electrical & Electronics + M.Sc. Mathematics — BITS Pilani Goa
[GitHub](https://github.com/Yp3RR) · [Email](mailto:yashpatil1492@gmail.com)

