import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.classify_messages import classify_message

# FastAPI App
app = FastAPI(
    title="WhatsApp Scam Detector API",
    description="API for classifying scam messages via Qdrant + Groq",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://web.whatsapp.com"],  # allow WhatsApp web
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Input schema
class InputMsg(BaseModel):
    text: str

# Root path
@app.get("/")
def root():
    return {"status": "running", "message": "Scam Detector API active"}

# Scam Classification Endpoint
@app.post("/classify")
def classify_text(payload: InputMsg):
    result = classify_message(payload.text)
    return {
        "input": payload.text,
        "classification": result
    }

# Main entry point
if __name__ == "__main__":
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=True)

