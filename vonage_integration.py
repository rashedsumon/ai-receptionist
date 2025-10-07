# vonage_integration.py
import os
from utils import get_env
import requests
import json

# The 'vonage' Python SDK is used for SMS and simple actions
try:
    import vonage
except Exception:
    vonage = None

VONAGE_API_KEY = get_env("VONAGE_API_KEY")
VONAGE_API_SECRET = get_env("VONAGE_API_SECRET")

def send_sms(to_number, text):
    """
    Send SMS using Vonage. Requires VONAGE_API_KEY and VONAGE_API_SECRET environment variables.
    """
    if vonage is None:
        return False, "vonage package not installed"
    if not VONAGE_API_KEY or not VONAGE_API_SECRET:
        return False, "Vonage credentials not provided"
    client = vonage.Client(key=VONAGE_API_KEY, secret=VONAGE_API_SECRET)
    sms = vonage.Sms(client)
    response = sms.send_message(
        {"from": "RE-Office", "to": to_number, "text": text}
    )
    return True, response

def simulate_inbound_call(session_id, caller_number, transcript):
    """
    Simulation helper for UI: pretend that a phone call came in, with given transcript (speech->text).
    In production this would be implemented as a webhook endpoint for Vonage Voice API events.
    """
    # This returns a dict similar to what your app will use downstream
    return {
        "session_id": session_id,
        "caller": caller_number,
        "transcript": transcript
    }

# For voice handling in production:
def note_about_voice():
    return (
        "Vonage Voice API requires a publicly reachable webhook (answer_url and event_url). "
        "Streamlit Cloud doesn't expose webhook endpoints; for production host a separate Flask/FastAPI endpoint "
        "and point Vonage to it, or use ngrok for local dev."
    )
