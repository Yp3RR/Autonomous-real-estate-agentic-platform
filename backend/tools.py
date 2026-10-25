# import random
# from datetime import datetime, timedelta
from backend.calendar_service import check_calendar_availability, book_calendar_appointment


# ─── Tool Definitions

TOOL_DEFINITIONS = [
    {
        "name": "check_availability",
        "description": "Check if a time slot is available for booking. Available slots are 10:00, 11:30, 13:00, 15:00, 16:30.Time in HH:MM 24hr format only. 10 AM = 10:00, 11:30 AM = 11:30, 1 PM = 13:00, 3 PM  = 15.30, 4.30 PM = 16.30. user may input time formats in other ways too, understand it properly. Always check availability before booking.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "time": {"type": "string", "description": "Time in HH:MM 24hr format e.g. 14:00"}
            },
            "required": ["date", "time"]
        }
    },
    {
        "name": "book_site_visit",
        "description": "Book a confirmed appointment on the calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Customer full name"},
                "phone": {"type": "string", "description": "Customer phone number"},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "time": {"type": "string", "description": "Time in HH:MM 24hr format"},
                "purpose": {"type": "string", "description": "Purpose of the appointment"}
            },
            "required": ["name", "phone", "date", "time"]
        }
    },
    {
        "name": "escalate_to_human",
        "description": "Escalate the conversation to a human sales representative.",
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Reason for escalation"
                }
            },
            "required": ["reason"]
        }
    },
    {
        "name": "log_lead",
        "description": "Log the lead data after conversation ends for CRM and analytics.",
        "parameters": {
            "type": "object",
            "properties": {
                "config_interest": {"type": "string"},
                "budget_range": {"type": "string"},
                "visit_booked": {"type": "boolean"},
                "follow_up_required": {"type": "boolean"},
                "objections_raised": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "interest_level": {
                    "type": "string",
                    "description": "hot | warm | cold"
                }
            },
            "required": ["config_interest", "visit_booked", "follow_up_required", "interest_level"]
        }
    }
]


# Simulated Tool Implementations

def check_availability(date: str, time: str) -> dict:
    return check_calendar_availability(date, time)


def book_site_visit(name: str, phone: str, date: str, time: str, purpose: str = "Appointment") -> dict:
    return book_calendar_appointment(name, phone, date, time, purpose)


def escalate_to_human(reason: str) -> dict:
    return {
        "escalated": True,
        "reason": reason,
        "message": "A sales representative will contact you within 2 hours."
    }


def log_lead(config_interest: str, visit_booked: bool, follow_up_required: bool,
             interest_level: str, budget_range: str = None, objections_raised: list = None) -> dict:
    return {
        "logged": True,
        "interest_level": interest_level,
        "config_interest": config_interest,
        "visit_booked": visit_booked,
        "follow_up_required": follow_up_required,
        "message": "Lead successfully logged to CRM."
    }


# Tool Router

def execute_tool(tool_name: str, tool_args: dict) -> dict:
    if tool_name == "check_availability":
        return check_availability(**tool_args)
    elif tool_name == "book_site_visit":
        return book_site_visit(**tool_args)
    elif tool_name == "escalate_to_human":
        return escalate_to_human(**tool_args)
    elif tool_name == "log_lead":
        return log_lead(**tool_args)
    else:
        return {"error": f"Unknown tool: {tool_name}"}