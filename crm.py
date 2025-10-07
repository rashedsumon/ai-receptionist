# crm.py
import csv
from pathlib import Path
from datetime import datetime

CRM_FILE = Path("crm_leads.csv")

def ensure_file():
    if not CRM_FILE.exists():
        with CRM_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp","customer_name","phone","intent","message","note"])

def log_lead(customer_name, phone, intent, message, note=""):
    ensure_file()
    with CRM_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow().isoformat()+"Z", customer_name, phone, intent, message, note])
