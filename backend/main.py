from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.models import ChatRequest, ChatResponse, AnalyticsRequest, LeadAnalytics

app = FastAPI(title="Northstar AI Agent", version="1.0.0")

# (frontend on Vercel to talk to this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten this to your Vercel URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return ChatResponse(
        session_id=request.session_id,
        response="Agent not yet implemented.",
        conversation_ended=False
    )


@app.post("/analytics", response_model=LeadAnalytics)
def analytics(request: AnalyticsRequest):
    return LeadAnalytics(session_id=request.session_id)


@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    from backend.session_store import clear_session as _clear
    _clear(session_id)
    return {"cleared": True, "session_id": session_id}