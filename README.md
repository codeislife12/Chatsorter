# ChatSorter

**Persistent memory API for chatbots and AI assistants.**

ChatSorter gives your bot the ability to remember users across sessions  names, preferences, relationships, and anything else that matters  without any changes to your core chat logic.

---

## How it works

Every message sent to `/process` is buffered and scored for importance. Every 5 messages a background summary is generated and stored. When a user returns, `/search` retrieves the most relevant memories automatically  ranked by semantic similarity, importance, and recency.

High-importance facts (allergies, names, preferences, relationships) are promoted to a cross-session master memory so they are never lost even across different chat sessions.

```
User sends message
       ↓
  POST /process       
       ↓
  Background server    ← summarizes every 5 messages
       ↓
  POST /search         
```

---

## Quickstart

### 1. Get an API key

Go to [chatsorter-website.vercel.app](https://chatsorter-website.vercel.app) and create a free account to get a key.

### 2. Store a message

```python
import requests

API_KEY = "your_api_key_here"
BASE_URL = "https://ungilled-loan-implosively.ngrok-free.dev"

requests.post(f"{BASE_URL}/process", json={
    "chat_id": "user_123_session_1",
    "message": "My name is Alice and I'm allergic to peanuts",
    "user_id": "user_123"
}, headers={"Authorization": f"Bearer {API_KEY}"})
```

### 3. Retrieve memories on next session

```python
result = requests.post(f"{BASE_URL}/search", json={
    "chat_id": "user_123_session_1",
    "query": "what do I know about this user",
    "user_id": "user_123"
}, headers={"Authorization": f"Bearer {API_KEY}"})

memories = result.json()["memories"]
for memory in memories:
    print(memory["summary"])
# → "Alice is allergic to peanuts and shellfish..."
```

### 4. Or use the combined endpoint

```python
# Store + retrieve in one call
result = requests.post(f"{BASE_URL}/chat", json={
    "chat_id": "user_123_session_1",
    "message": "What should I eat tonight?",
    "user_id": "user_123"
}, headers={"Authorization": f"Bearer {API_KEY}"})

memories  = result.json()["retrieved_memories"]
# Inject memories into your system prompt
```

---

## API Reference

### `POST /process`
Store a message. Returns immediately, summarization runs in the background.

**Request**
```json
{
  "chat_id": "string",
  "message": "string",
  "user_id": "string"
}
```

**Response**
```json
{
  "success": true,
  "data": {
    "message_count": 5,
    "buffer_count": 5,
    "importance_score": 8.5,
    "queue_depth": 1
  }
}
```

---

### `POST /search`
Search stored memories for a user.

**Request**
```json
{
  "chat_id": "string",
  "query": "string",
  "user_id": "string"
}
```

**Response**
```json
{
  "success": true,
  "memories": [
    {
      "summary": "Alice is 28, lives in Seattle, works as a software engineer.",
      "importance_score": 8.5,
      "similarity": 0.91,
      "composite_score": 0.87,
      "source": "master",
      "timestamp": "2025-01-01T00:00:00Z"
    }
  ],
  "total_found": 3,
  "returned": 3
}
```

---

### `POST /chat`
Store a message and retrieve relevant memories in a single call. Recommended for most integrations.

**Request**
```json
{
  "chat_id": "string",
  "message": "string",
  "user_id": "string"
}
```

**Response**
```json
{
  "success": true,
  "message_stored": true,
  "retrieved_memories": [...],
  "debug": {
    "buffer_count": 3,
    "messages_until_summary": 2,
    "queue_depth": 0
  }
}
```

---

### `GET /health`
Check server status and queue depth.

```json
{
  "status": "healthy",
  "llm_ready": true,
  "queue_depth": 0,
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### `GET /queue`
Check how many summaries are pending.

```json
{
  "queue_depth": 2,
  "status": "busy",
  "llm_ready": true
}
```

---

## Injecting memories into your system prompt

```python
def build_system_prompt(memories: list) -> str:
    if not memories:
        return "You are a helpful assistant."
    
    memory_text = "\n".join([f"- {m['summary']}" for m in memories])
    
    return f"""You are a helpful assistant.

What you remember about this user:
{memory_text}

Use this context naturally in your responses."""
```

---

## Memory scoring

Every message is scored 0-10 for importance before storage:

| Signal | Example | Boost |
|--------|---------|-------|
| Allergy / medical | "I'm allergic to peanuts" | +3.5 |
| Name | "My name is Alice" | +3.0 |
| Age | "I'm 28 years old" | +3.0 |
| Job | "I'm a software engineer" | +2.5 |
| Location | "I live in Seattle" | +2.5 |
| Pet | "My dog is named Max" | +2.0 |
| Preference | "My favorite movie is..." | +1.5 |

Memories scoring above 8.0 are promoted to master memory automatically.

---

## Examples

See the [`/examples`](./examples) folder for:
- `basic_integration.py`  minimal working integration
- `system_prompt_injection.py`  how to inject memories into your LLM prompt

---

## FAQ

**Does it store raw messages?**
No. Only summaries are stored. Raw messages are held in memory briefly for summarization then discarded.

**What happens if the LLM is busy?**
`/process` returns immediately regardless. Summarization is queued and runs in the background.

**How many messages before a summary is generated?**
Default is every 5 messages. Configurable via `/update-settings`.

**Is it open source?**
The API is closed source. Examples and documentation are open.

---

## Get started

[Get a free beta key](https://chatsorter-website.vercel.app)
