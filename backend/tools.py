import random
from datetime import datetime, timedelta

# ─── Tool Definitions

TOOL_DEFINITIONS = [
    {
        "name": "check_availability",
        "description": "Check available site visit slots for a given date and flat configuration.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Preferred visit date in YYYY-MM-DD format"
                },
                "config": {
                    "type": "string",
                    "description": "Flat configuration requested: '2BHK' or '3BHK'"
                }
            },
            "required": ["date", "config"]
        }
    },
    {
        "name": "book_site_visit",
        "description": "Book a site visit for the customer at Northstar One, Sector 79 Gurugram.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Customer's full name"},
                "phone": {"type": "string", "description": "Customer's phone number"},
                "date": {"type": "string", "description": "Visit date in YYYY-MM-DD format"},
                "config": {"type": "string", "description": "2BHK or 3BHK"}
            },
            "required": ["name", "phone", "date", "config"]
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

def check_availability(date: str, config: str) -> dict:
    try:
        visit_date = datetime.strptime(date, "%Y-%m-%d")
        if visit_date < datetime.now():
            return {"available": False, "reason": "Date is in the past."}
    except ValueError:
        return {"available": False, "reason": "Invalid date format."}

    available = random.random() > 0.2
    slots = ["10:00 AM", "12:00 PM", "3:00 PM"] if available else []

    return {
        "available": available,
        "date": date,
        "config": config,
        "slots": slots,
        "reason": None if available else "No slots available on this date."
    }


def book_site_visit(name: str, phone: str, date: str, config: str) -> dict:
    success = random.random() > 0.15

    if success:
        return {
            "booked": True,
            "booking_id": f"NS-{random.randint(1000, 9999)}",
            "name": name,
            "date": date,
            "config": config,
            "location": "Northstar One, Sector 79, Gurugram",
            "message": f"Site visit confirmed for {name} on {date}."
        }
    else:
        return {
            "booked": False,
            "message": "Booking failed due to a system error. Please try a different date or contact our team directly."
        }


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