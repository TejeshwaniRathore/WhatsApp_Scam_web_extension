import json
from qdrant_client.models import PointStruct, VectorParams, Distance
from embed_model import embed_text
from qdrant_client_setup import get_client

COLLECTION = "scam_messages_1"
BATCH_SIZE = 100  # Adjust if needed; smaller = safer

client = get_client()
# 1) Ensure collection exists
def create_collection():
    if COLLECTION not in client.get_collections().collections:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )
        print("Collection created.")
    else:
        print("Collection already exists.")

# 2) Load JSON
def load_data():
    with open("qdrant_payloads.json", "r") as f:
        return json.load(f)

# 3) Embed + Upload in batches
def upload():
    data = load_data()
    print(f"Loaded {len(data)} items from JSON.")
    total_uploaded = 0

    for batch_start in range(0, len(data), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(data))
        batch = data[batch_start:batch_end]
        points = []

        for idx, item in enumerate(batch, start=batch_start):
            text = item["text"]
            label = item.get("label", "unknown")

            vector = embed_text(text)

            points.append(
                PointStruct(
                    id=idx,
                    vector=vector,
                    payload={"text": text, "label": label}
                )
            )

        client.upsert(collection_name=COLLECTION, points=points)
        total_uploaded += len(points)
        print(f"Uploaded batch {batch_start // BATCH_SIZE + 1}: {len(points)} points (total: {total_uploaded})")

    print(f"Done! Total uploaded: {total_uploaded}")

if __name__ == "__main__":
    # create_collection()
    upload()
