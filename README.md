# Eunoia AI Chat Service

Python-based service providing supportive AI chat using Google Gemini 2.0 Flash with built-in crisis detection and scope enforcement for mental health safety.

## Tech Stack
- Python 3.x, FastAPI (or Flask, depending on implementation)
- Google Generative AI (Gemini 2.0 Flash)
- Uvicorn / Gunicorn, CORS

## Endpoints
- `GET /health` – service status
- `POST /chat` – chat with context `{ message, conversation_history? }`

## Safety Features
- Crisis detection using regex patterns (e.g., suicide ideation, self-harm)
- India-specific resources returned on crisis (Aasra, Vandrevala, SNEHA)
- Scope enforcement for non-mental-health queries

## Quick Start
1. Prerequisites: Python 3.10+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Environment variables:
   - GEMINI_API_KEY=your_api_key
   - PORT=8080
4. Run locally (example):
   ```bash
   python application.py
   ```

## Request Example (`/chat`)
```json
{
  "message": "I'm feeling overwhelmed lately",
  "conversation_history": [
    {"role":"user","content":"I'm stressed"},
    {"role":"assistant","content":"I'm here to listen."}
  ]
}
```

## Deployment
- Dockerized via `Dockerfile`. Deploy on any Python host. Ensure API keys and CORS are configured.
