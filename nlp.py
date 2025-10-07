# nlp.py
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
from pathlib import Path

MODEL_PATH = Path("nlp_model.joblib")
VECT_PATH = Path("tfidf_vect.joblib")

# Predefined keywords for quick rule-based intent detection
KEYWORDS = {
    "book_viewing": ["book", "viewing", "appointment", "visit", "schedule", "seeing", "show me", "see the"],
    "availability": ["available", "is the", "still available", "vacant", "vacancy"],
    "connect_agent": ["connect", "agent", "human", "representative", "speak to", "transfer"],
    "sell_process": ["sell", "sell my home", "valuation", "valuation", "how to sell"],
    "pricing": ["price", "rent", "cost", "how much"],
    "general": ["hello", "hi", "info", "information", "question"]
}

def rule_intent(text):
    t = text.lower()
    for intent, kw_list in KEYWORDS.items():
        for kw in kw_list:
            if kw in t:
                return intent
    return None

class HybridNLU:
    def __init__(self):
        self.model = None
        self.vect = None
        # Try to load pretrained components if exist
        try:
            import joblib
            if MODEL_PATH.exists() and VECT_PATH.exists():
                self.model = joblib.load(MODEL_PATH)
                self.vect = joblib.load(VECT_PATH)
        except Exception:
            self.model = None
            self.vect = None

    def train_from_csv(self, path, text_col_candidates=None, label_col_candidates=None):
        df = pd.read_csv(path)
        # Guess columns
        text_col = None
        label_col = None
        text_candidates = text_col_candidates or ["message", "text", "query", "customer_message", "utterance"]
        label_candidates = label_col_candidates or ["label", "intent", "category"]
        for c in text_candidates:
            if c in df.columns:
                text_col = c
                break
        for c in label_candidates:
            if c in df.columns:
                label_col = c
                break
        if text_col is None or label_col is None:
            return False, "Could not find text/label columns. Falling back to rule based."
        X = df[text_col].astype(str).fillna("")
        y = df[label_col].astype(str).fillna("")
        vect = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
        Xv = vect.fit_transform(X)
        model = LogisticRegression(max_iter=1000)
        model.fit(Xv, y)
        # persist
        import joblib
        joblib.dump(model, MODEL_PATH)
        joblib.dump(vect, VECT_PATH)
        self.model = model
        self.vect = vect
        return True, "Trained classifier from CSV."

    def predict_intent(self, text):
        # Rule-based first
        r = rule_intent(text)
        if r:
            return r, 0.9
        # ML fallback
        if self.model and self.vect:
            x = self.vect.transform([text])
            pred = self.model.predict_proba(x)
            idx = pred.argmax()
            label = self.model.classes_[idx]
            confidence = float(pred[0, idx])
            return str(label), confidence
        # Fallback generic
        return "unknown", 0.0
