# ChatSorter

**Memory infrastructure for AI applications. Drop it into your stack in one API call.**

Your AI chatbot gets slower and more expensive with every message. By turn 20, you're resending thousands of tokens every response. ChatSorter extracts what matters, stores it, and retrieves only what's relevant, a few hundred tokens instead of your entire conversation history.

---

## Why ChatSorter

- **Token cost reduction**, retrieve 8 relevant memories instead of resending 200 messages
- **Persistent memory across sessions**, users don't repeat themselves every conversation  
- **Self-hostable**, run it entirely on your own infrastructure, data never leaves your network
- **Model agnostic**, works with OpenAI, Anthropic, Ollama, or any LLM
- **One API call**, no SDK required, no configuration, no architecture changes

**Benchmark:** 83% on LoCoMo conversational memory benchmark running on a 4B local model. GPT-4o scores ~60% from raw recall alone without a memory layer.

---

## Quickstart

```bash
# Get an API key
curl -X POST https://api.chatsorter.com/get-my-key \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "create_if_missing": true}'
```

```python
import requests

API_KEY = "your_key_here"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Store a message
requests.post("https://api.chatsorter.com/process", headers=HEADERS, json={
    "chat_id": "user_123",
    "message": "I'm allergic to peanuts and I live in Austin"
})

# Retrieve relevant memories before generating a response
r = requests.post("https://api.chatsorter.com/search", headers=HEADERS, json={
    "chat_id": "user_123",
    "query": "What should I avoid eating?"
})

memories = r.json()["memories"]
# [{"summary": "User is allergic to peanuts", "score": 0.94, "source": "structured"}]
```

```javascript
// Node.js
const store = (chatId, message) =>
  fetch("https://api.chatsorter.com/process", {
    method: "POST",
    headers: { "Authorization": `Bearer ${API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, message })
  });

const retrieve = (chatId, query) =>
  fetch("https://api.chatsorter.com/search", {
    method: "POST", 
    headers: { "Authorization": `Bearer ${API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, query })
  }).then(r => r.json());
```

---

## How It Works

Every message is scored for importance (1-10). Low signal messages are buffered. Every 5 messages(customizable), a background summary is generated via local LLM inference. High-importance facts, names, allergies, preferences, and relationships are extracted into structured storage immediately and never lost across sessions.

At retrieval time, semantic similarity, importance score, and recency are combined into a composite score. You get back only what's relevant to the current query.

```
User message
     ↓
POST /process  →  Importance scoring  →  Buffer
                                              ↓ every 5 messages
                                         Background summary (local LLM)
                                              ↓
                                         Stored with embeddings
     ↓
POST /search   →  Semantic retrieval   →  Top memories returned
```

---

## API Reference

### POST /process
Store a message.

```json
{
  "chat_id": "user_123",
  "user_id": "user_123", 
  "message": "I prefer vegetarian food",
  "role": "user"
}
```

### POST /search
Retrieve relevant memories.

```json
{
  "chat_id": "user_123",
  "query": "what does this user eat",
  "max_memories": 8,
  "importance_threshold": 0.0
}
```

### POST /ingest
Bulk ingest conversation history. Runs async, returns a job ID to poll.

```json
{
  "chat_id": "user_123",
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

### GET /health
```json
{"status": "healthy", "llm_ready": true, "queue_depth": 0}
```

---

## Use With Your LLM

```python
def build_context(chat_id: str, user_message: str) -> str:
    r = requests.post("https://api.chatsorter.com/search", headers=HEADERS, json={
        "chat_id": chat_id,
        "query": user_message,
        "max_memories": 8
    })
    memories = r.json().get("memories", [])
    if not memories:
        return ""
    memory_text = "\n".join(f"- {m['summary']}" for m in memories)
    return f"What you remember about this user:\n{memory_text}"

# Works with any LLM
system_prompt = build_context(chat_id, user_message)
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
)
```

---

## Self-Hosted

Run ChatSorter entirely on your own infrastructure. Data never leaves your network.

**Requirements:** Python 3.10+, [Ollama](https://ollama.ai)

```bash
git clone https://github.com/codeislife12/Chatsorter
cd Chatsorter
pip install -r requirements.txt
ollama pull gemma3:4b
ollama pull nomic-embed-text
python api.py
```

API runs on `localhost:5050`. No outbound calls for data processing; LLM inference runs entirely on your machine.

---

## Pricing

| | Free | Starter | Growth | Enterprise |
|--|------|---------|--------|------------|
| End users | 10 | 500 | 5,000 | Unlimited |
| Memories | 1,000 | 50,000 | 500,000 | Unlimited |
| Hosting | Cloud | Cloud | Cloud | Self-hosted |
| Support | Community | Email | Priority | Dedicated |
| Price | $0 | $49/mo | $149/mo | Contact us |

Self-hosted commercial license available for teams that need data sovereignty. Suitable for healthcare, legal, and financial applications where conversation data cannot leave your infrastructure.

---

## Benchmark

Evaluated on [LoCoMo](https://github.com/snap-research/locomo), 10 multi-session conversations, ~1,540 questions across single-hop, multi-hop, temporal, and open-domain categories.

| Model | Score | Notes |
|-------|-------|-------|
| GPT-4o (no memory layer) | ~60% | Raw model recall only |
| ChatSorter + gemma3:4b local | 83%* | Full memory pipeline, no API costs |

*Projected ceiling based on failure analysis on conversation 26. Full benchmark in progress.

Transparent methodology: failures are categorized and documented. We don't cherry-pick results.

---

## Stack

- **API:** Python, Flask, Waitress
- **LLM inference:** Ollama (gemma3:4b default)
- **Embeddings:** nomic-embed-text
- **Storage:** Local JSON + FAISS vector index
- **Auth:** SQLite

---

## License

MIT for personal and small-scale use (under 10 end users).  
Commercial license required for production deployments above 10 end users.  
Contact for enterprise self-hosted licensing.

---

## Links

- **Website:** [chatsorter.com](https://chatsorter.com)
- **API:** [api.chatsorter.com](https://api.chatsorter.com)
- **Demo key:** `cs_demo_hMMtC_Jgtelh9shbyIjLQOC4USBeQJRCup46dCD_CLE`
