# WhatsApp Scam Detector 🛡️

An AI-powered system to detect and classify scams in WhatsApp messages using vector embeddings, Qdrant database, and Groq LLM.

## 🎯 Features

✅ **Real-time Scam Detection** - Detects 6 scam categories in real-time  
✅ **Hybrid AI Architecture** - Embeddings + Vector Search + LLM  
✅ **Chrome Extension** - One-click installation for WhatsApp Web  
✅ **FastAPI Backend** - High-performance REST API with Swagger docs  
✅ **Vector Database** - Qdrant for semantic similarity search  
✅ **Groq LLM Integration** - Fast inference with Llama 3.1-8b  

## 📊 Scam Categories Detected

- 🆔 **KYC Scams** - "Verify your identity now"
- 🔐 **OTP Scams** - "Enter OTP to verify"
- 💼 **Job Scams** - Fake job offers
- 💰 **Loan Scams** - "Quick loan approved"
- 📦 **Parcel Scams** - "Claim your package"
- 🏦 **Banking/Investment** - Fake investment schemes

## 🏗️ System Architecture

```
User Message
    ↓
Chrome Extension (Intercept)
    ↓
FastAPI Backend (/classify)
    ↓
Sentence Transformer (Embed)
    ↓
Qdrant Vector DB (Search Top 5 Similar)
    ↓
Groq LLM (Final Classification)
    ↓
Result: SCAM/SAFE + Category + Reason
```

## 🚀 Quick Start

### Prerequisites
- Python 3.14+
- Chrome/Chromium browser
- API keys (Qdrant, Groq)

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/WhatsApp_Scam_web_extension.git
cd WhatsApp_Scam_web_extension

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Configure Environment

Create `.env` in project root:

```bash
QDRANT_URL=https://your-qdrant-url:6333
QDRANT_API_KEY=your_qdrant_api_key
GROQ_API_KEY=your_groq_api_key
```

### 3. Run Backend

```bash
uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000
```

API available at: **http://localhost:8000/docs**

### 4. Load Chrome Extension

1. Open `chrome://extensions/`
2. Enable **Developer mode** (top-right)
3. Click **Load unpacked**
4. Select `chrome_extension/` folder

## 📡 API Endpoints

### POST `/classify`
Classify a single message

**Request:**
```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"text":"Your parcel is held. Pay ₹70 to claim"}'
```

**Response:**
```json
{
  "label": "SCAM",
  "category": "parcel",
  "reason": "Typical parcel phishing with payment demand",
  "confidence": 0.92
}
```

### GET `/`
Health check

```bash
curl http://localhost:8000/
```

### GET `/docs`
Interactive API documentation (Swagger UI)

## 🧩 Chrome Extension Usage

1. Go to WhatsApp Web (https://web.whatsapp.com)
2. Open any chat
3. Hover over a message
4. Extension highlights **SCAM** messages in red
5. Click to see classification details

## 📂 Project Structure

```
WhatsApp_Scam_web_extension/
├── .env                          # API keys (not committed)
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
├── Dockerfile                    # Docker configuration
├── requirements.txt              # Root dependencies
│
├── backend/
│   ├── server.py                 # FastAPI app
│   ├── classify_messages.py      # Classification logic
│   ├── embed_model.py            # Sentence Transformer
│   ├── qdrant_client_setup.py    # Qdrant client
│   ├── config.py                 # Configuration
│   ├── requirements.txt          # Backend dependencies
│   │
│   ├── data/
│   │   ├── raw/spam.csv          # Original dataset
│   │   └── processed/cleaned_dataset.csv
│   │
│   ├── scripts/
│   │   ├── 01_clean_data.py
│   │   ├── 02_prepare_payloads.py
│   │   └── 03_ingest_to_qdrant.py
│   │
│   └── notebooks/
│       └── Data_Cleaning.ipynb
│
├── chrome_extension/
│   ├── manifest.json             # Extension config
│   ├── content.js                # Message interceptor
│   ├── background.js        # Background worker
|
│
├── tests/
│   ├── test_classify.py
│   ├── test_embed.py
│   └── test_api.py
│
└── docs/
    ├── SETUP.md
    ├── API.md
    └── DEPLOYMENT.md
```

## 🌐 Deployment

### Option 1: Deploy on Render (Recommended - Free tier)

1. Push code to GitHub
2. Go to https://render.com
3. Create new **Web Service**
4. Connect GitHub repo
5. Set:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `uvicorn backend.server:app --host 0.0.0.0 --port 8000`
6. Add environment variables (.env values)
7. Deploy!

Your API: `https://your-app.onrender.com/docs`

### Option 2: Deploy with Docker

```bash
# Build image
docker build -t scam-detector .

# Run container
docker run -p 8000:8000 \
  -e QDRANT_URL="https://..." \
  -e QDRANT_API_KEY="..." \
  -e GROQ_API_KEY="..." \
  scam-detector
```

### Option 3: Deploy on Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set QDRANT_URL="https://..."
heroku config:set QDRANT_API_KEY="..."
heroku config:set GROQ_API_KEY="..."

# Push code
git push heroku main
```

## 📊 Data Pipeline

```
1. Raw Data (spam.csv)
   ↓
2. Data Cleaning (01_clean_data.py)
   - Handle encoding issues
   - Remove duplicates
   - Clean text
   ↓
3. Payload Preparation (02_prepare_payloads.py)
   - Convert CSV to JSON
   ↓
4. Embedding & Ingestion (03_ingest_to_qdrant.py)
   - Generate embeddings
   - Upload to Qdrant
```

Run pipeline:
```bash
cd backend/scripts
bash run_pipeline.sh
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_classify.py -v

# With coverage
pytest --cov=backend tests/
```

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI, Uvicorn |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector DB | Qdrant |
| LLM | Groq (Llama 3.1-8b) |
| Frontend | Chrome Extension (JavaScript) |
| Deployment | Render, Docker, Heroku |

## 📝 API Documentation

Full API docs available at `/docs` endpoint (Swagger UI) when backend is running.

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍💻 Author

**Your Name** - [@your_github](https://github.com/YOUR_USERNAME)

## 🙋 Support

For issues and questions:
- Open GitHub Issue
- Check existing documentation in `/docs`
- Review API docs at `/docs` endpoint

---

**⭐ If this project helped you, please give it a star!**
