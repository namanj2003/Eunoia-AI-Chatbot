from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Eunoia AI Chat Service",
    description="Mental health chatbot API using Google Gemini",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Request/Response Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_history: List[Message] = []

# System prompt with fallback for out-of-domain
def create_system_prompt() -> str:
    return """
You are Eunoia, a compassionate mental health support chatbot serving users in India.

**CRITICAL RULES:**
- Only respond to queries about mental health, emotions, stress, motivation, or well-being.
- If the user's message is about another topic (e.g., sports, politics, technology, finance, academics, coding, etc.), politely say:
"I'm here to support mental health and emotional well-being. Is there something about your feelings you'd like to discuss?"
- NEVER mention US crisis resources (911, 988, 1-800 numbers, 741741)
- NEVER provide phone numbers - crisis resources are handled separately
- When someone mentions suicide/self-harm explicitly, express concern briefly but DO NOT list numbers
- "I'm feeling depressed" is NOT a crisis - respond with empathy and support

**Your purpose:**
- Support users with depression, anxiety, stress, and emotional challenges
- Listen with empathy and validate feelings
- Ask clarifying questions
- Suggest coping strategies
- Be warm and conversational

**Communication style:**
- Warm, empathetic, concise (2-4 sentences)
- Validate emotions before offering solutions
- Never start with disclaimers

**Remember:** You're in India. Most users need empathy, not crisis intervention.
"""

def check_for_crisis(message: str):
    """Check for EXPLICIT crisis keywords"""
    crisis_keywords = [
        r'\bsuicid', r'\bkill\s+(my)?self\b', r'\bwant\s+to\s+die\b',
        r'\bend\s+my\s+life\b', r'\bself[\s-]?harm\b', r'\bcut\s+(my)?self\b',
        r'\bhurt\s+(my)?self\b', r'\boverdose\b', r'\bending\s+(it|things|everything)\b',
        r'\bplan(ning)?\s+to\s+(die|kill)', r'\bbetter\s+off\s+dead\b',
        r'\bno\s+reason\s+to\s+live\b', r'\bno\s+longer\s+want\s+to\s+(be\s+here|exist|live)\b'
    ]
    import re
    message_lower = message.lower()
    for pattern in crisis_keywords:
        if re.search(pattern, message_lower, re.IGNORECASE):
            resources = {
                "message": "I'm really concerned about what you're sharing. Your safety is the top priority right now.",
                "india_resources": {
                    "aasra": {"name": "Aasra (Mumbai)", "phone": "+91 9820466726", "available": "24/7"},
                    "vandrevala": {"name": "Vandrevala Foundation", "phone": "1860 266 2345 / 1800 233 3330", "available": "24/7"},
                    "sneha": {"name": "SNEHA (Chennai)", "phone": "+91 44 2464 0050", "available": "24/7"},
                }
            }
            return True, resources
    return False, None

# Minimal blocklist for clear, direct requests (not context-based)
blocked_patterns = [
    r"\b(solve|write|do|complete|answer)\s+(my\s+)?(homework|assignment|project|essay|test|code)\b",
    r"\b(debug|fix|write|solve)\s+(my\s+)?(code|program|script|algorithm)\b",
    r"\b(calculate|compute|find|solve)\s+(my\s+)?(math|equation|problem)\b",
    r"\b(build|create|develop)\s+(my\s+)?(app|website|api|database)\b",
    r"\b(give|send|provide)\s+(me\s+)?(money|loan|investment|job|career|stock|crypto|bitcoin)\b"
]

import re
def is_blocked_query(message: str) -> bool:
    message_lower = message.lower()
    for pattern in blocked_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return True
    return False

def generate_ai_response(user_message: str, conversation_history: List[Message]) -> str:
    try:
        # Build chat history
        chat_history = []
        for msg in conversation_history[-10:]:
            chat_history.append({
                "role": "user" if msg.role == "user" else "model",
                "parts": [msg.content]
            })
        # Start chat
        chat = gemini_model.start_chat(history=chat_history)
        # Generate response
        system_prompt = create_system_prompt()
        full_prompt = f"{system_prompt}\n\nUser message: {user_message}\n\nRespond naturally and empathetically."
        response = chat.send_message(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating AI response: {str(e)}")
        return "I apologize, but I'm having trouble processing your message right now. Could you please try again."

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Eunoia AI Chat Service",
        "model": "Google Gemini 2.0 Flash",
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": "Google Gemini 2.0 Flash",
        "inference_available": GEMINI_API_KEY is not None
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        message_lower = request.message.lower()
        print(f"\n[INFO] Received message: {message_lower}")

        # Check for crisis
        is_crisis, crisis_resources = check_for_crisis(request.message)
        if is_crisis:
            print("[CRISIS] Crisis detected - showing Indian resources")
            crisis_message = f"""{crisis_resources['message']}

🆘 **IMMEDIATE HELP AVAILABLE IN INDIA:**

**National 24/7 Helplines:**
• Aasra (Mumbai): +91 9820466726
• Vandrevala Foundation: 1860 266 2345 or 1800 233 3330
• SNEHA (Chennai): +91 44 2464 0050 / +91 44 2464 0060

**Emergency:** Police: 100 | Ambulance: 102/108

📞 Trained counselors can help you right now. You don't have to face this alone."""
            return {
                "success": True,
                "response": crisis_message,
                "is_crisis": True,
                "crisis_resources": crisis_resources
            }

        # Block only direct, non-contextual requests
        if is_blocked_query(request.message):
            print("[BLOCKED] Found blocked pattern")
            return {
                "success": True,
                "response": "I'm specifically designed to support mental health and emotional well-being. I can't help with that task.\n\nIs there something about your feelings or mental well-being you'd like to discuss?",
                "is_crisis": False,
                "crisis_resources": None
            }

        # Let Gemini handle all proper queries
        print("[ACCEPTED] Passing to Gemini for context understanding")
        ai_response = generate_ai_response(request.message, request.conversation_history)
        return {
            "success": True,
            "response": ai_response,
            "is_crisis": False,
            "crisis_resources": None
        }

    except Exception as e:
        print(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# # For local development
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=7860)
