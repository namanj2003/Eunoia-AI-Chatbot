import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CHAT_SERVICE_URL", "http://127.0.0.1:7860")

def quick_test(message):
    print(f"\n📝 Testing message: '{message}'\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message, "conversation_history": []},
            timeout=30
        )
        
        result = response.json()
        
        print("="*70)
        print(f"👤 USER: {message}")
        print("-"*70)
        print(f"🤖 BOT:  {result.get('response', 'No response')}")
        print("="*70)
        print(f"\n✅ Success: {result.get('success', False)}")
        print(f"⚠️  Crisis: {result.get('is_crisis', False)}")
        
        if result.get('crisis_resources'):
            print(f"📞 Crisis Resources: Available")
        print()
        
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to {BASE_URL}")
        print("\nMake sure the server is running:")
        print("   uvicorn application:app --reload --port 7860")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use command line argument
        message = " ".join(sys.argv[1:])
    else:
        # Default test message
        message = "I've been feeling anxious about my studies"
    
    quick_test(message)
