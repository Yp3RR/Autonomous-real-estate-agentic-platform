from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    conversation_ended: bool = False


class AnalyticsRequest(BaseModel):
    session_id: str


class LeadAnalytics(BaseModel):
    session_id: str
    lead_score: Optional[int] = None
    config_interest: Optional[str] = None
    budget_range: Optional[str] = None
    preferred_language: Optional[str] = None
    visit_booked: bool = False
    visit_date: Optional[str] = None
    follow_up_required: bool = False
    objections_raised: list[str] = []
    escalated_to_human: bool = False
    conversation_summary: Optional[str] = None