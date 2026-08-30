# **Northstar AI Agent**

An agentic AI sales assistant for Northstar One, a residential project in Sector 79, Gurugram. 
Built with FastAPI and Google Gemini — the agent autonomously qualifies leads, answers project queries, 
books site visits via real tool calls, and generates structured lead analytics after every conversation.

### Status: *Active development — backend complete, frontend and production hardening in progress.*

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

## Tech Stack

| Layer | Tool                    |
|---|-------------------------|
| LLM | Google Gemini 3.6 Flash |
| Backend | FastAPI (Python)        |
| Session Memory | In-memory session store |
| Data Validation | Pydantic v2             |
| Frontend | HTML + CSS + Vanilla JS |
| Deploy (backend) | Render                  |
| Deploy (frontend) | Vercel                  |

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

- Session memory is in-memory — restarting the server clears all sessions (persistent DB planned)
- Booking and availability are simulated — no real calendar or CRM integration
- The agent never reveals it is an AI unless directly and sincerely asked
- All project facts (pricing, area, amenities) are sourced only from the system prompt — no external data fetch

---
## Known Limitations

- In-memory sessions do not survive server restarts
- No rate limiting on API endpoints (planned)
- No authentication on session endpoints — any client can clear any session by ID
- Analytics generation makes an additional Gemini API call — adds ~2s latency

---
## Roadmap

### In Progress
- [ ] Frontend UI (chat interface + analytics modal)

### Planned
- [ ] **Persistent storage** — SQLite or PostgreSQL to survive server restarts
- [ ] **Structured logging** — JSON logs with session ID, tool calls, latency, errors
- [ ] **Input validation + guardrails** — prompt injection detection, input length limits
- [ ] **Eval script** — automated test suite scoring agent behaviour across 10+ scenarios
- [ ] **Rate limiting** — per-session request throttling
- [ ] **Observability** — Helicone integration for LLM call tracing and token usage dashboard
- [ ] **Prompt versioning** — A/B eval comparing v1 vs v2 system prompt performance
- [ ] **Containerization** — Docker + docker-compose for local and production
- [ ] **Deployment** — Render (backend) + Vercel (frontend)

---

## AI Tools Used

- **Google Gemini 2.0 Flash** — LLM powering the agent and analytics pipeline
- **Claude (Anthropic)** — used during development for code assistance, architecture decisions, and prompt engineering iteration

---

## Author

**Yash Patil**
B.E. Electrical & Electronics + M.Sc. Mathematics — BITS Pilani Goa
[GitHub](https://github.com/Yp3RR) · [Email](mailto:yashpatil1492@gmail.com)

