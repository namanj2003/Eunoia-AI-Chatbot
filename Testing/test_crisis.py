import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CHAT_SERVICE_URL", "http://127.0.0.1:7860")

def test_crisis():
    message = "I've been having thoughts about harming myself"
    
    print(f"🧪 Testing Crisis Detection")
    print(f"🔗 Endpoint: {BASE_URL}/chat")
    print(f"📝 Message: '{message}'\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": message,
                "conversation_history": []
            },
            timeout=30
        )
        
        result = response.json()
        
        print(result.get('response', 'No response'))
        print("="*70)
        
        print(f"\n✅ Success: {result.get('success', False)}")
        print(f"⚠️  Crisis Detected: {result.get('is_crisis', False)}")
        
        if result.get('crisis_resources'):
            print("\n📞 Crisis Resources Provided:")
            india_resources = result['crisis_resources'].get('india_resources', {})
            for key, value in india_resources.items():
                name = value.get('name', key)
                phone = value.get('phone', 'N/A')
                available = value.get('available', '24/7')
                print(f"   • {name}: {phone} ({available})")
        
        print()
        
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to {BASE_URL}")
        print("\nMake sure the server is running:")
        print("   uvicorn application:app --reload --port 7860")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_crisis()
