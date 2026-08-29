# **Northstar AI Agent**

An agentic AI sales assistant for Northstar One, a residential project in Sector 79, Gurugram. 
Built with FastAPI and Google Gemini — the agent autonomously qualifies leads, answers project queries, 
books site visits via real tool calls, and generates structured lead analytics after every conversation.

### Status: *Active development — backend complete, frontend and production hardening in progress.*

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