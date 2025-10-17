import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variable or default to localhost
BASE_URL = os.getenv("CHAT_SERVICE_URL", "http://127.0.0.1:7860")

def chat_session():
    print("EUNOIA AI - MENTAL HEALTH SUPPORT".center(70))
    print("\nType your message and press Enter to chat.")
    print("Commands:")
    print("  - 'quit' or 'exit' to end session")
    print("  - 'clear' to clear conversation history")
    print("  - 'history' to view conversation history")
    print("\n" + "-"*70 + "\n")
    
    conversation_history = []
    
    while True:
        # Get user input
        user_message = input("You: ").strip()
        
        if not user_message:
            continue
        
        # Handle commands
        if user_message.lower() in ['quit', 'exit']:
            print("\n👋 Goodbye! Take care of yourself.")
            break
        
        if user_message.lower() == 'clear':
            conversation_history = []
            print("\n🔄 Conversation history cleared.\n")
            continue
        
        if user_message.lower() == 'history':
            print("\n📜 Conversation History:")
            if not conversation_history:
                print("   (empty)")
            else:
                for i, msg in enumerate(conversation_history, 1):
                    role_emoji = "👤" if msg['role'] == 'user' else "🤖"
                    preview = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
                    print(f"   {i}. {role_emoji} {msg['role'].capitalize()}: {preview}")
            print()
            continue
        
        # Send message to API
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={
                    "message": user_message,
                    "conversation_history": conversation_history
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Display bot response
            if result.get('success', False):
                print(f"\n🤖 Eunoia: {result['response']}\n")
                
                # Show crisis warning if detected
                if result.get('is_crisis', False):
                    print("⚠️  CRISIS RESOURCES HAVE BEEN PROVIDED ⚠️")
                    if result.get('crisis_resources'):
                        print("📞 Please reach out to these resources for immediate help.\n")
                
                # Update conversation history
                conversation_history.append({
                    "role": "user",
                    "content": user_message
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": result['response']
                })
            else:
                print(f"\n❌ Error: {result.get('response', 'Unknown error')}\n")
            
            print("-"*70 + "\n")
            
        except requests.exceptions.ConnectionError:
            print("\n❌ ERROR: Cannot connect to chatbot API")
            print(f"Make sure the server is running at: {BASE_URL}")
            print("\nTo start the server, run:")
            print("   uvicorn application:app --reload --port 7860\n")
            break
        except requests.exceptions.Timeout:
            print("\n Request timed out. Please try again.\n")
        except requests.exceptions.HTTPError as e:
            print(f"\n❌ HTTP Error: {e}\n")
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}\n")

if __name__ == "__main__":
    print(f"Connecting to: {BASE_URL}\n")
    chat_session()
