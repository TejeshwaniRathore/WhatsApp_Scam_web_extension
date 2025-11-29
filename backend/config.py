import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")     # <--- PUT in .env
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")  # <--- PUT in .env

QDRANT_COLLECTION = "scam_messages"

EMBED_MODEL = "all-MiniLM-L6-v2"
EMBED_DIM = 384

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
