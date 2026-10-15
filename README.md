# ChatSorter

**Persistent memory for AI applications, without the cost of resending entire conversations.**

ChatSorter is a memory API for developers building AI chatbots and agents. It stores conversation context, extracts useful facts, and retrieves relevant memories when your application needs them.

Instead of sending your entire conversation history with every request, your application can retrieve a smaller set of relevant information and pass it to its LLM.

- **Persistent memory:** Retain useful information across conversations and sessions.
- **Context compression:** Retrieve relevant memories instead of repeatedly sending long conversation histories.
- **Two-endpoint integration:** Send messages to `/process` and retrieve memories through `/search`.
- **Model agnostic:** Use ChatSorter with OpenAI, Anthropic, Ollama, or another LLM.
- **Cloud or self-hosted:** Use the hosted API or run the local version on your own infrastructure.

## Quickstart

Get an API key at [chatsorter.com](https://chatsorter.com/), then install the Python dependency:

```bash
pip install requests
```

Store a message:

```python
import os
import requests

API_KEY = os.environ["CHATSorter_API_KEY"]
BASE_URL = "https://api.chatsorter.com"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

user_id = "user_123"

response = requests.post(
    f"{BASE_URL}/process",
    headers=HEADERS,
    json={
        "chat_id": user_id,
        "message": "I prefer vegetarian food.",
    },
    timeout=30,
)
response.raise_for_status()
```

Retrieve relevant memories before generating the next response:

```python
response = requests.post(
    f"{BASE_URL}/search",
    headers=HEADERS,
    json={
        "chat_id": user_id,
        "query": "What food does this user prefer?",
    },
    timeout=30,
)
response.raise_for_status()

memories = response.json().get("memories", [])
memory_context = "\n".join(
    f"- {memory['summary']}" for memory in memories
)
```

Add `memory_context` to your LLM's prompt. Your application controls how retrieved memories are used.

See the [online documentation](https://chatsorter.com/) for current API details, deployment instructions, and pricing.

## Links

- [Website](https://chatsorter.com/)
- [Cloud pricing](https://chatsorter.com/pricing)
- [Live demo](https://chatsorter.com/demo)
- [Changelog](https://chatsorter.com/changelog.html)
- [Source code](https://github.com/codeislife12/Chatsorter)
