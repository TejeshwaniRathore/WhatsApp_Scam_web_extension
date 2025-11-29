# backend/make_qdrant_payloads.py
import pandas as pd
import uuid
import json
import re
from tqdm import tqdm

# Simple keyword-based category assignment.
CATEGORY_KEYWORDS = {
    "KYC": ["kyc", "verify account", "verification", "document", "identity"],
    "OTP": ["otp", "one time", "one-time", "verification code", "code is"],
    "LOAN": ["loan", "interest rate", "apply loan", "instant loan", "loan sanction"],
    "JOB": ["interview", "job offer", "hiring", "congratulations you are selected", "work from home"],
    "PARCEL": ["delivery", "parcel", "courier", "track your order", "shipment", "tracking id"],
    "BANK": ["bank", "account", "debit", "credit", "upi", "neft", "ifsc"],
    "INVESTMENT": ["investment", "bitcoin", "crypto", "mutual fund", "returns", "guaranteed return"]
}

def assign_category(text: str) -> str:
    t = text.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in t:
                return cat
    # fallback based on label heuristics
    return "GENERAL_SCAM"

def id_from_uuid():
    return str(uuid.uuid4())

def load_and_make_json(csv_path: str, out_json: str, text_col="text", label_col="label"):
    df = pd.read_csv(csv_path)
    if text_col not in df.columns:
        raise ValueError(f"Column {text_col} not in CSV")
    rows = []
    for _, r in tqdm(df.iterrows(), total=len(df)):
        text = str(r[text_col]).strip()
        if not text:
            continue
        label = r[label_col] if label_col in df.columns else None
        cat = assign_category(text)
        rows.append({
            "id": id_from_uuid(),
            "text": text,
            "category": cat,
            "label": str(label) if label is not None else None,
            "explanation": f"auto-category:{cat}"
        })
    with open(out_json, "w", encoding="utf8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(rows)} items to {out_json}")

if __name__ == "__main__":
    # Example run
    load_and_make_json("backend/cleaned_dataset.csv", "qdrant_payloads.json")
