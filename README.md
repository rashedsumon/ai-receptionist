# AI Receptionist — Real Estate (Streamlit app)

## Overview
This app demonstrates an AI-powered receptionist for a real estate business:
- Intent detection (NLP)
- Booking/viewing scheduling (local calendar JSON)
- Simulated Vonage SMS + (illustrative) Vonage call handling
- CRM lead logging

**Dataset**: Expected CSV: `/kaggle/input/real-estate-customer-care-dataset/Real Estate - Customer Care.csv`  
If that path is not available (e.g., on Streamlit Cloud), upload the CSV through the app UI or place it under `data/Real_Estate_Customer_Care.csv`.

## Quick start (local)
1. Create virtual env with Python 3.11
2. `pip install -r requirements.txt`
3. Export env vars (example):
   - `VONAGE_API_KEY`, `VONAGE_API_SECRET`, `VONAGE_APPLICATION_ID`, `VONAGE_PRIVATE_KEY` (if using voice)
   - `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` (for email notifications)
4. Run `streamlit run app.py`

## Webhooks & Vonage inbound calls
- Vonage will POST webhooks for inbound calls / events. **Streamlit Cloud does not provide a public webhook endpoint** for Vonage. For development, either:
  - Run `vonage_webhook.py` locally + expose with `ngrok` and register the URL with Vonage.
  - Deploy a small Flask/FastAPI app on a public host (e.g., Railway, Render, Heroku), and forward required events to the Streamlit app or the CRM.

## Deployment to Streamlit Cloud
- Add repository to Streamlit Cloud.
- Add required environment variables via Streamlit Cloud UI (Secrets).
- Upload dataset to the app via the UI or include in repo.

## Notes & Limitations
- This repo implements a hybrid intent system (rule-based + simple classifier). For production, replace with a robust NLU (Rasa, Dialogflow, or a transformer-based classifier).
- Real voice handling and streaming STT typically require a webhook/voice application on a public server. See `vonage_integration.py` for sample methods and instructions.

## File map
- `app.py` — streamlit UI and main orchestration
- `nlp.py` — intent detection, training helpers
- `vonage_integration.py` — Vonage wrappers and simulations
- `calendar_store.py` — appointment storage / retrieval
- `crm.py` — lead logging
- `utils.py` — helper utilities

## Dataset
Place the Kaggle CSV at `data/Real_Estate_Customer_Care.csv` or upload it with the UI. The app will attempt to auto-detect message column names.

