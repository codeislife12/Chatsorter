"""
ChatSorter — Basic Integration Example
Get a free API key at: chatsorter-website.vercel.app
"""

import requests

API_KEY  = "your_api_key_here"
BASE_URL = "https://your-chatsorter-url.com"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def store_message(chat_id: str, user_id: str, message: str) -> dict:
    """Send a message to ChatSorter for storage and summarization."""
    resp = requests.post(f"{BASE_URL}/process", json={
        "chat_id": chat_id,
        "user_id": user_id,
        "message": message
    }, headers=HEADERS)
    return resp.json()


def get_memories(chat_id: str, user_id: str, query: str) -> list:
    """Retrieve the most relevant memories for a query."""
    resp = requests.post(f"{BASE_URL}/search", json={
        "chat_id": chat_id,
        "user_id": user_id,
        "query":   query
    }, headers=HEADERS)
    data = resp.json()
    return data.get("memories", [])


def chat(chat_id: str, user_id: str, message: str) -> dict:
    """Store a message and retrieve relevant memories in one call."""
    resp = requests.post(f"{BASE_URL}/chat", json={
        "chat_id": chat_id,
        "user_id": user_id,
        "message": message
    }, headers=HEADERS)
    return resp.json()


if __name__ == "__main__":
    CHAT_ID = "demo_chat_001"
    USER_ID = "demo_user_001"

    # Simulate a user sharing personal details over several messages
    messages = [
        "Hi! My name is Alice.",
        "I'm 28 years old and I live in Seattle.",
        "I work as a software engineer.",
        "I'm allergic to peanuts and shellfish — really important.",
        "My dog is named Max, he's 5 years old.",
    ]

    print("Storing messages...")
    for msg in messages:
        result = store_message(CHAT_ID, USER_ID, msg)
        print(f"  Stored: '{msg[:40]}...' | importance={result['data']['importance_score']}")

    print("\nWaiting for background summarization...")
    import time
    time.sleep(30)  # Give the background worker time to summarize

    print("\nRetrieving memories...")
    memories = get_memories(CHAT_ID, USER_ID, "tell me about this user")
    for mem in memories:
        print(f"  [{mem['source']}] {mem['summary']}")
        print(f"  importance={mem['importance_score']} similarity={mem['similarity']}")
