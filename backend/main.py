from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.models import ChatRequest, ChatResponse, AnalyticsRequest, LeadAnalytics
from backend.agent import run_agent
from backend.session_store import clear_session
from backend.analytics import generate_analytics

app = FastAPI(title="Northstar AI Agent", version="1.0.0")

# (frontend on Vercel to talk to this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = run_agent(request.session_id, request.message)
    return ChatResponse(
        session_id=request.session_id,
        response=result["response"],
        conversation_ended=result["conversation_ended"]
    )


@app.post("/analytics", response_model=LeadAnalytics)
def analytics(request: AnalyticsRequest):
    data = generate_analytics(request.session_id)
    return LeadAnalytics(**data)


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    clear_session(session_id)
    return {"cleared": True, "session_id": session_id}