from .qdrant_client_setup import get_client
from .embed_model import embed_text
from groq import Groq
import json
import os

client = get_client()
COLLECTION = "scam_messages_1"

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print(os.getenv("GROQ_API_KEY"))
def classify_message(message: str):
    """
    Hybrid classifier:
    1. Embed message using local model
    2. Retrieve nearest similar scams from Qdrant
    3. LLM classifies into SCAM/SAFE + category + reason
    """

    # STEP 1 — Embed the message
    vector = embed_text(message)

    # STEP 2 — Retrieve Top Similar Points
    search_result = client.query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=5
    )

    # Collect examples for LLM
    examples = []
    for hit in search_result.points:
        examples.append({
            "text": hit.payload.get("text", ""),
            "category": hit.payload.get("label", "")
        })

    # STEP 3 — Build LLM Prompt
    prompt = f"""
You are a WhatsApp Scam Detection AI.

Your job:
1. Detect if a message is SCAM or SAFE.
2. If scam, identify category: kyc, otp, loan, job, parcel.
3. Give a short reason for classification.

User Message:
{message}

Here are similar known examples from the scam database:
{json.dumps(examples, indent=2)}

You MUST respond ONLY in valid JSON:
{{
  "label": "SCAM" or "SAFE",
  "category": "kyc"|"otp"|"loan"|"job"|"parcel"|null,
  "reason": "short explanation"
}}
"""

    # STEP 4 — LLM Classification (Groq)
    llm_output = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    # STEP 5 — Parse JSON
    try:
        response_text = llm_output.choices[0].message.content.strip()
        result = json.loads(response_text)
    except Exception:
        # fallback if json fails
        result = {
            "label": "SAFE",
            "category": None,
            "reason": "LLM returned invalid JSON. Marking safe by default."
        }

    return result

# def classify_message(message):
#     vector = embed_text(message)

#     search_result = client.query_points(
#         collection_name=COLLECTION,
#         query=vector,
#         limit=5
#     )

#     top_labels = [hit.payload["label"] for hit in search_result.points]

#     prompt = f"""
# You are a scam detection classifier.
# User message: {message}
# Nearest messages have labels: {top_labels}

# Return ONLY one label: kyc, otp, job, loan, parcel, or safe.
# """

#     llm_output = groq_client.chat.completions.create(
#         model="llama-3.1-8b-instant",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     return llm_output.choices[0].message.content.strip()
