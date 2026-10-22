import json
import pathlib
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from backend.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, REDIRECT_URI

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Token stored as JSON file for now — will migrate to DB in Phase 2
TOKEN_PATH = pathlib.Path(__file__).parent / "token.json"

CLIENT_CONFIG = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [REDIRECT_URI]
    }
}

# IST offset — make this configurable per business in Phase 4
IST = timezone(timedelta(hours=5, minutes=30))


# ─── OAuth Flow ───────────────────────────────────────────────────────────────

def get_auth_url() -> str:
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.code_verifier = None
    # Ensure flow doesn't enforce PKCE verifier mismatch issues in simple server setups
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        # include_granted_scopes=True
    )
    return auth_url


def exchange_code_for_token(authorization_response_url: str) -> bool:
    """Exchange full callback URL for access + refresh tokens and store them."""
    try:
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        flow.code_verifier = None
        # Pass the full callback URL so requests_oauthlib can extract the code and validate properly
        flow.fetch_token(authorization_response=authorization_response_url)
        creds = flow.credentials

        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": list(creds.scopes) if creds.scopes else SCOPES
        }
        TOKEN_PATH.write_text(json.dumps(token_data))
        return True
    except Exception as e:
        print(f"[Calendar] Token exchange failed: {e}")
        return False


# ─── Internal Helpers ─────────────────────────────────────────────────────────

def _get_credentials() -> Credentials:
    """Load credentials from token file, refresh if expired."""
    if not TOKEN_PATH.exists():
        raise ValueError("No token found. Business client must complete OAuth setup first.")

    token_data = json.loads(TOKEN_PATH.read_text())
    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=token_data["scopes"]
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Persist refreshed token
        token_data["token"] = creds.token
        TOKEN_PATH.write_text(json.dumps(token_data))

    return creds


def _get_service():
    """Build and return Google Calendar API service."""
    return build("calendar", "v3", credentials=_get_credentials())


def _parse_datetime(date: str, time: str) -> datetime:
    """Parse date (YYYY-MM-DD) and time (HH:MM) into IST-aware datetime."""
    dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    return dt.replace(tzinfo=IST)


# ─── Calendar Tools ───────────────────────────────────────────────────────────

def check_calendar_availability(date: str, time: str) -> dict:
    """Check if a given date+time slot is free on the business calendar."""
    try:
        service = _get_service()

        dt_start = _parse_datetime(date, time)
        dt_end = dt_start + timedelta(hours=1)

        body = {
            "timeMin": dt_start.isoformat(),
            "timeMax": dt_end.isoformat(),
            "items": [{"id": "primary"}]
        }

        result = service.freebusy().query(body=body).execute()
        busy_slots = result["calendars"]["primary"]["busy"]

        if busy_slots:
            return {
                "available": False,
                "reason": "That slot is already booked. Please choose a different time."
            }

        return {
            "available": True,
            "date": date,
            "time": time,
            "message": f"Slot is available on {date} at {time}."
        }

    except ValueError as e:
        return {"available": False, "reason": str(e)}
    except Exception as e:
        print(f"[Calendar] Availability check failed: {e}")
        return {"available": False, "reason": "Could not check availability. Please try again."}


def book_calendar_appointment(name: str, phone: str, date: str, time: str, purpose: str = "Appointment") -> dict:
    """Create a Google Calendar event to confirm the appointment."""
    try:
        service = _get_service()

        dt_start = _parse_datetime(date, time)
        dt_end = dt_start + timedelta(hours=1)

        event = {
            "summary": f"{purpose} — {name}",
            "description": f"Booked via AI Agent\nClient Name: {name}\nPhone: {phone}",
            "start": {"dateTime": dt_start.isoformat(), "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": dt_end.isoformat(), "timeZone": "Asia/Kolkata"},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 60},
                    {"method": "popup", "minutes": 15}
                ]
            }
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()

        return {
            "booked": True,
            "event_id": created_event["id"],
            "event_link": created_event.get("htmlLink"),
            "name": name,
            "date": date,
            "time": time,
            "message": f"Appointment confirmed for {name} on {date} at {time}."
        }

    except ValueError as e:
        return {"booked": False, "message": str(e)}
    except Exception as e:
        print(f"[Calendar] Booking failed: {e}")
        return {"booked": False, "message": "Booking failed. Please try again or contact us directly."}