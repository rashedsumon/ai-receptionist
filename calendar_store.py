# calendar_store.py
import json
from pathlib import Path
from datetime import datetime

DB = Path("calendar_db.json")

def load_db():
    if not DB.exists():
        return []
    return json.loads(DB.read_text())

def save_db(data):
    DB.write_text(json.dumps(data, indent=2))

def list_slots():
    return load_db()

def add_booking(customer_name, phone, property_id, start_time_iso, notes="", agent=""):
    data = load_db()
    booking = {
        "id": len(data)+1,
        "customer_name": customer_name,
        "phone": phone,
        "property_id": property_id,
        "start_time": start_time_iso,
        "notes": notes,
        "agent": agent,
        "created_at": datetime.utcnow().isoformat()+"Z"
    }
    data.append(booking)
    save_db(data)
    return booking

def is_slot_conflict(start_time_iso):
    # naive: check exact same ISO collisions
    data = load_db()
    return any(b["start_time"] == start_time_iso for b in data)
