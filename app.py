# app.py
import streamlit as st
import pandas as pd
from pathlib import Path
from nlp import HybridNLU
from vonage_integration import send_sms, simulate_inbound_call, note_about_voice
from calendar_store import add_booking, is_slot_conflict, list_slots
from crm import log_lead
from utils import get_env
import datetime

st.set_page_config(page_title="AI Receptionist — Real Estate", layout="wide")

st.title("🏢 AI Receptionist — Real Estate (Demo)")

# Sidebar: dataset loading
st.sidebar.header("Dataset / NLU")
kaggle_path = "/kaggle/input/real-estate-customer-care-dataset/Real Estate - Customer Care.csv"
uploaded = None

st.sidebar.write("The app will attempt to read the Kaggle path you provided. If it's missing, upload the CSV or use demo data.")
if Path(kaggle_path).exists():
    st.sidebar.success("Found Kaggle CSV path.")
    df = pd.read_csv(kaggle_path)
else:
    uploaded = st.sidebar.file_uploader("Upload dataset CSV (optional)", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
    else:
        st.sidebar.info("No CSV provided — using small demo samples.")
        df = pd.DataFrame({
            "message": [
                "Is the apartment on Main Street still available?",
                "I want to book a viewing for 5 PM Friday",
                "Please connect me to an agent",
                "How do I sell my house?"
            ],
            "label": ["availability","book_viewing","connect_agent","sell_process"]
        })

st.sidebar.write("Dataset preview:")
st.sidebar.dataframe(df.head(10))

# Initialize NLU
nlu = HybridNLU()
if not nlu.model:
    trained, msg = nlu.train_from_csv(Path("data/Real_Estate_Customer_Care.csv") if Path("data/Real_Estate_Customer_Care.csv").exists() else Path("demo.csv")) if False else (False, "No training run")
    # Try training from uploaded df if it has label
    if "label" in df.columns and "message" in df.columns:
        from tempfile import NamedTemporaryFile
        fp = NamedTemporaryFile(delete=False, suffix=".csv")
        df.to_csv(fp.name, index=False)
        trained, msg = nlu.train_from_csv(fp.name, text_col_candidates=["message"], label_col_candidates=["label"])
        if trained:
            st.sidebar.success("Trained a lightweight intent classifier from supplied CSV.")
        else:
            st.sidebar.warning(msg)

st.header("Simulate an Incoming Call (Demo)")
with st.form("call_sim"):
    caller = st.text_input("Caller number", value="+8801XXXXXXXXX")
    transcript = st.text_area("Speech-to-text transcript (what caller said)", value="I want to book a viewing for next Tuesday at 5pm for property ID 123")
    submit = st.form_submit_button("Process Call")
if submit:
    event = simulate_inbound_call("sess-demo-1", caller, transcript)
    st.write("Incoming call event:")
    st.json(event)

    # NLU
    intent, conf = nlu.predict_intent(transcript)
    st.markdown(f"**Detected intent:** `{intent}` (confidence {conf:.2f})")

    # Simple slot extraction (very naive)
    import re
    dt_match = re.search(r"\b(\d{1,2}\s?(am|pm|AM|PM)|tomorrow|next \w+|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", transcript, re.IGNORECASE)
    prop_match = re.search(r"(property|apartment|flat|unit)\s*(?:ID)?\s*#?\s*(\d+)", transcript, re.IGNORECASE)
    proposed_time = dt_match.group(0) if dt_match else None
    prop_id = prop_match.group(2) if prop_match else "unknown"

    st.write("Extracted details:")
    st.write({"proposed_time": proposed_time, "property_id": prop_id})

    # Branch based on intent
    if intent == "book_viewing" or "book" in transcript.lower():
        # For demo we convert naive time to ISO now + 1 day if vague
        now = datetime.datetime.utcnow()
        start_iso = (now + datetime.timedelta(days=1)).isoformat() + "Z"
        # check conflict
        if is_slot_conflict(start_iso):
            st.error("Slot conflict — cannot book at that exact time (demo).")
        else:
            booking = add_booking("Unknown Caller", caller, prop_id, start_iso, notes=transcript)
            log_lead("Unknown Caller", caller, intent, transcript, note="Booked via AI receptionist")
            st.success("Booking created (demo).")
            st.json(booking)
            # send sms if configured
            sms_text = f"Your viewing is booked for {start_iso} for property {prop_id}. — Real Estate Office"
            ok, resp = send_sms(caller, sms_text)
            if ok:
                st.info("SMS sent (Vonage).")
            else:
                st.warning(f"SMS not sent: {resp}")
    elif intent == "availability":
        st.info("Responded: Checking property availability (demo).")
        # Log & optionally sms
        log_lead("Unknown Caller", caller, intent, transcript, note="Asked about availability")
        st.write("Response suggestion: 'Yes — it's available. Would you like to book a viewing?'")
    elif intent == "connect_agent":
        st.info("Routing to agent (demo).")
        log_lead("Unknown Caller", caller, intent, transcript, note="Requested agent transfer")
        st.write("Action suggestion: Ring agent or create a callback task.")
    elif intent == "sell_process":
        st.info("Explained selling process (demo).")
        log_lead("Unknown Caller", caller, intent, transcript, note="Interested in selling")
        st.write("Action suggestion: send seller guide and schedule valuation.")
    else:
        st.info("Intent not recognized confidently; logged for follow-up.")
        log_lead("Unknown Caller", caller, intent, transcript, note="Unknown intent")

st.markdown("---")
st.header("Calendar — Bookings")
bookings = list_slots()
if bookings:
    st.dataframe(bookings)
else:
    st.info("No bookings yet (demo).")

st.markdown("---")
st.header("Notes on Vonage Voice & Production")
st.write(note_about_voice())
st.write("For production voice / STT, host a webhook endpoint publicly and configure Vonage `answer_url` and `event_url`. Streamlit Cloud cannot receive Vonage webhook pushes directly.")
