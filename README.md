# ChatSorter

**Memory infrastructure for AI applications.**

ChatSorter gives AI chatbots and agents persistent memory through a simple API. It scores conversation messages, extracts useful facts, summarizes history, and retrieves relevant context when your application needs it.

Instead of resending an entire conversation every time your model generates a response, retrieve the memories relevant to the current message. This helps reduce context size, API costs, and unnecessary repetition while allowing your application to remember information across sessions.

## Why ChatSorter?

- **Lower context costs:** Retrieve relevant memories instead of repeatedly sending hundreds of old messages.
- **Persistent memory:** Keep user preferences, personal details, and conversation history available across sessions.
- **Automatic processing:** Importance scoring, summarization, and fact extraction run without requiring users to manage their own memories.
- **Model agnostic:** Use ChatSorter with OpenAI, Anthropic, Ollama, or other LLM providers.
- **Cloud or self-hosted:** Use the hosted API or run the local version on your own infrastructure.
- **Simple integration:** Store messages and retrieve context through HTTP endpoints.

## Quickstart

Get an API key at [chatsorter.com](https://chatsorter.com/).

Install the Python dependency:

```bash
pip install requests
```

### 1. Store a message

```python
import os
import requests

API_KEY = os.environ["CHATSORTER_API_KEY"]
BASE_URL = "https://api.chatsorter.com"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

chat_id = "user_123"

response = requests.post(
    f"{BASE_URL}/process",
    headers=HEADERS,
    json={
        "chat_id": chat_id,
        "message": "I'm allergic to peanuts and I live in Austin.",
    },
    timeout=30,
)

response.raise_for_status()
print(response.json())
```

### 2. Retrieve relevant memories

Before generating a response, search for information related to the user's latest message.

```python
response = requests.post(
    f"{BASE_URL}/search",
    headers=HEADERS,
    json={
        "chat_id": chat_id,
        "query": "What should I avoid eating?",
        "max_memories": 8,
    },
    timeout=30,
)

response.raise_for_status()
memories = response.json().get("memories", [])

for memory in memories:
    print(memory["summary"])
```

Example output:

```text
User is allergic to peanuts.
User lives in Austin.
```

The exact results depend on the messages processed and the retrieval configuration.

### 3. Add memories to your LLM prompt

```python
memory_context = "\n".join(
    f"- {memory['summary']}"
    for memory in memories
)

messages = [
    {
        "role": "system",
        "content": (
            "Use the following information when relevant:\n"
            f"{memory_context}"
        ),
    },
    {
        "role": "user",
        "content": "What should I avoid eating?",
    },
]
```

Pass these messages to your preferred LLM provider. ChatSorter manages memory storage and retrieval; your application remains responsible for generating the response.

For a live walkthrough, visit the [ChatSorter demo](https://chatsorter.com/demo).

## How It Works

ChatSorter processes conversation messages through three layers.

```text
New conversation message
          |
          v
     POST /process
          |
          v
  Importance scoring
          |
          v
    Rolling buffer
          |
          v
  Narrative summaries
          |
          v
  Structured fact extraction
          |
          v
  Persistent memory storage
          |
          v
     POST /search
          |
          v
  Relevant memories returned
          |
          v
  Your application's LLM
```

### Layer 1: Rolling buffer

Messages accumulate in a rolling buffer until the configured number of messages has been reached. This reduces the need to summarize every low-value message independently.

The default summary interval is five messages.

### Layer 2: Narrative summaries

Conversation messages are condensed into summaries that preserve useful context without retaining every message in the prompt.

Summaries are stored with importance scores and embeddings. Retrieval considers relevance, importance, and recency, allowing the system to prioritize useful information over outdated or low-value details.

### Layer 3: Structured fact extraction

ChatSorter extracts useful facts from individual messages, including names, preferences, relationships, and other information that may matter in future conversations.

Facts include confidence information and subject attribution, so details about different people can be distinguished. Conflicting information can be retained for historical context while newer values take precedence in retrieval.

This combination allows ChatSorter to retain both specific facts and the broader context of a conversation.

## API Reference

All examples below use the hosted API at `https://api.chatsorter.com`.

Authenticate using your API key in the `Authorization` header:

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### `POST /process`

Submit a message for processing. ChatSorter evaluates its importance and makes it available to the memory processing pipeline.

Request:

```json
{
  "chat_id": "user_123",
  "user_id": "user_123",
  "message": "I prefer vegetarian food.",
  "role": "user",
  "session_date": "2026-09-11"
}
```

Example response:

```json
{
  "success": true,
  "importance_score": 6.5,
  "message_count": 3,
  "facts": [
    {
      "type": "diet",
      "value": "vegetarian",
      "confidence": 0.88
    }
  ]
}
```

The response fields shown above are illustrative. Check the live API behavior for the exact schema and processing status.

### `POST /search`

Retrieve memories relevant to a query.

Request:

```json
{
  "chat_id": "user_123",
  "query": "What does this user eat?",
  "max_memories": 8,
  "importance_threshold": 0.0
}
```

Example response:

```json
{
  "success": true,
  "memories": [
    {
      "summary": "User prefers vegetarian food",
      "score": 0.94,
      "source": "structured"
    },
    {
      "summary": "User is allergic to peanuts and lives in Austin",
      "score": 0.87,
      "source": "summary"
    }
  ]
}
```

The `max_memories` parameter controls how many memories to request. The `importance_threshold` parameter can be used to filter lower-importance results where supported by the deployed configuration.

### `POST /sdk/v1`

Use the combined endpoint when you want to submit a message and request relevant memories in one operation.

Request:

```json
{
  "chat_id": "user_123",
  "user_id": "user_123",
  "message": "What restaurants do you recommend?",
  "retrieve_memories": true,
  "session_date": "2026-09-11"
}
```

This endpoint is useful when integrating memory into an existing chatbot request flow.

### `POST /ingest`

Bulk ingest an existing conversation history.

Request:

```json
{
  "chat_id": "user_123",
  "messages": [
    {
      "role": "user",
      "content": "My name is Alex."
    },
    {
      "role": "assistant",
      "content": "Nice to meet you, Alex."
    },
    {
      "role": "user",
      "content": "I prefer vegetarian food."
    }
  ],
  "messages_per_summary": 5
}
```

Bulk ingestion runs asynchronously and returns a job identifier for checking progress.

### `GET /ingest/status/{job_id}`

Check the status of a bulk ingestion job using the identifier returned by `/ingest`.

### `GET /health`

Check the API's health and processing status.

Example response:

```json
{
  "status": "healthy",
  "llm_ready": true,
  "queue_depth": 0
}
```

Consult the deployed service for the exact health response fields.

## Use With Your LLM

ChatSorter does not require you to replace your existing model or rewrite your chatbot. Retrieve the relevant memories and add them to your existing prompt.

For example, the retrieval portion of a Python integration can be kept separate from the model provider:

```python
def build_context(chat_id: str, user_message: str) -> str:
    response = requests.post(
        f"{BASE_URL}/search",
        headers=HEADERS,
        json={
            "chat_id": chat_id,
            "query": user_message,
            "max_memories": 8,
        },
        timeout=30,
    )
    response.raise_for_status()

    memories = response.json().get("memories", [])

    if not memories:
        return ""

    memory_text = "\n".join(
        f"- {memory['summary']}"
        for memory in memories
    )

    return (
        "Relevant information from previous conversations:\n"
        f"{memory_text}"
    )
```

Use the returned context with your existing LLM call. For example, with the OpenAI Python SDK:

```python
from openai import OpenAI

client = OpenAI()

memory_context = build_context(chat_id, user_message)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": memory_context or "No relevant memories were found.",
        },
        {
            "role": "user",
            "content": user_message,
        },
    ],
)
```

Install the OpenAI SDK separately if you use this example:

```bash
pip install openai
```

You can use the same retrieval function with other model providers. The retrieved memories are ordinary text that can be included in a system prompt or other context field supported by your model.

## Self-Hosted

ChatSorter can also run on your own infrastructure using local model inference.

A local deployment is useful when you want more control over data storage, model selection, and infrastructure costs.

### Requirements

- Python 3.10 or newer
- Ollama
- A compatible local language model
- A compatible embedding model

### Setup

The exact installation commands depend on the files and dependencies included in the current repository. Once the deployment requirements are installed, download the models used by your configuration.

For example:

```bash
ollama pull gemma3:4b
ollama pull nomic-embed-text
```

Configure ChatSorter to use your local Ollama instance and start the API using the entry point provided by your checkout.

The API's default local address is `http://localhost:5050`.

In a correctly configured local deployment, conversation processing and inference can run on your infrastructure without sending conversation data to the hosted ChatSorter API. Review any external integrations and network settings before using sensitive data.

For commercial self-hosted deployments, see the licensing information below or contact [chatsorter@gmail.com](mailto:chatsorter@gmail.com).

## Benchmarks

ChatSorter has been evaluated on [LoCoMo](https://github.com/snap-research/locomo), a benchmark for long-term conversational memory.

For benchmark methodology, model configurations, and updated results, see the [ChatSorter changelog](https://chatsorter.com/changelog).

## Pricing

ChatSorter offers a free cloud plan and paid plans for applications with larger usage requirements.

Pricing and plan limits can change. For current prices, retrieval limits, storage allowances, and hosting options, see the [pricing page](https://chatsorter.com/pricing).

For commercial self-hosted licensing, contact [chatsorter@gmail.com](mailto:chatsorter@gmail.com).

## Technology

ChatSorter uses the following technologies in its current implementation:

- **API:** Python, Flask, and Waitress
- **Local inference:** Ollama
- **Embeddings:** `nomic-embed-text`
- **Storage:** Local JSON files and FAISS vector indexes
- **Authentication:** SQLite and Firebase

The exact configuration depends on whether you use the hosted service or run ChatSorter locally.

## License

ChatSorter's licensing terms depend on how you use the software.

The stated terms permit personal use and deployments with fewer than 10 end users. Production deployments above that limit require a commercial license under the applicable licensing terms.

For enterprise and self-hosted commercial licensing, contact [chatsorter@gmail.com](mailto:chatsorter@gmail.com).

Review the repository's `LICENSE` file and any applicable commercial agreement before deploying the software.

## Links

- **Website:** [chatsorter.com](https://chatsorter.com/)
- **API:** [api.chatsorter.com](https://api.chatsorter.com/)
- **Demo:** [chatsorter.com/demo](https://chatsorter.com/demo)
- **Pricing:** [chatsorter.com/pricing](https://chatsorter.com/pricing)
- **Changelog and benchmarks:** [chatsorter.com/changelog](https://chatsorter.com/changelog)
- **Source code:** [GitHub repository](https://github.com/codeislife12/Chatsorter)

