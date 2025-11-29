# backend/embed_texts.py
import os
import json
from tqdm import tqdm
from typing import List
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODE = os.getenv("EMBEDDING_MODE", "local")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

def embed_with_sentence_transformer(texts: List[str], model_name="all-MiniLM-L6-v2"):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    embs = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return [e.astype("float32").tolist() for e in embs]

def embed_with_openai(texts: List[str], model="text-embedding-3-small"):
    import openai
    openai.api_key = OPENAI_API_KEY
    # OpenAI can accept batch; for large sets chunk them
    embs = []
    CHUNK = 10
    for i in tqdm(range(0, len(texts), CHUNK)):
        batch = texts[i:i+CHUNK]
        resp = openai.Embedding.create(model=model, input=batch)
        for d in resp["data"]:
            embs.append(d["embedding"])
    return embs

def main(input_json="qdrant_payloads.json", out_emb_json="qdrant_vectors.json"):
    with open(input_json, "r", encoding="utf8") as f:
        items = json.load(f)
    texts = [it["text"] for it in items]
    if EMBEDDING_MODE == "openai" and OPENAI_API_KEY:
        vectors = embed_with_openai(texts)
    else:
        vectors = embed_with_sentence_transformer(texts)
    # combine ids+vectors+payloads for Qdrant upsert
    out = []
    for it, v in zip(items, vectors):
        out.append({
            "id": it["id"],
            "vector": v,
            "payload": {
                "text": it["text"],
                "category": it.get("category"),
                "label": it.get("label"),
                "explanation": it.get("explanation")
            }
        })
    with open(out_emb_json, "w", encoding="utf8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"Saved {len(out)} vector entries to {out_emb_json}")

if __name__ == "__main__":
    main()
