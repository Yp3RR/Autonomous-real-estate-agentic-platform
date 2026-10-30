import json
import pathlib
from datetime import datetime, timedelta, timezone
import urllib.parse
import requests

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
    """Manually construct Google OAuth URL without PKCE baggage."""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent"
    }
    query_string = urllib.parse.urlencode(params)
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"


def exchange_code_for_token(code: str) -> bool:
    """Directly trade auth code for tokens via Google's token endpoint."""
    try:
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        }

        response = requests.post(token_url, data=payload)
        token_json = response.json()

        if response.status_code != 200:
            print(f"[Calendar] Token exchange API error: {token_json}")
            return False

        # Build clean token structure for Google Credentials class compatibility
        token_data = {
            "token": token_json.get("access_token"),
            "refresh_token": token_json.get("refresh_token"),
            "token_uri": token_url,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "scopes": SCOPES
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

AVAILABLE_SLOTS = ["10:00", "11:30", "13:00", "15:00", "16:30"]
def _normalize_time(time: str) -> str:
    """Convert any time format to HH:MM 24hr."""
    for fmt in ["%H:%M", "%I:%M %p", "%I:%M%p", "%I %p"]:
        try:
            return datetime.strptime(time.strip().upper(), fmt).strftime("%H:%M")
        except ValueError:
            continue
    return time

def check_calendar_availability(date: str, time: str) -> dict:
    print(f"[Calendar] check_availability called with date={date} time={time}", flush=True)
    time = _normalize_time(time)
    print(f"[Calendar] normalized time={time}, available slots={AVAILABLE_SLOTS}", flush=True)
    # First check if time is within allowed slots
    if time not in AVAILABLE_SLOTS:
        return {
            "available": False,
            "reason": f"Appointments are only available at: {', '.join(AVAILABLE_SLOTS)}. Please choose one of these times."
        }
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