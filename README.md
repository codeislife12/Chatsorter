# ChatSorter

**Memory infrastructure for AI applications. Drop it into your stack in one API call.**

Your AI chatbot gets slower and more expensive with every message. By turn 20, you're resending thousands of tokens every response. ChatSorter extracts what matters, stores it, and retrieves only what's relevant — a few hundred tokens instead of your entire conversation history.

---

## Why ChatSorter

- **Token cost reduction** — retrieve 8 relevant memories instead of resending 200 messages
- **Persistent memory across sessions** — users don't repeat themselves every conversation
- **Self-hostable** — run it entirely on your own infrastructure, data never leaves your network
- **Model agnostic** — works with OpenAI, Anthropic, Ollama, or any LLM
- **One API call** — no SDK required, no configuration, no architecture changes

---

## Quickstart

```bash
# Get a free API key at chatsorter.com
# Or use the demo key below to test immediately
```

```python
import requests

API_KEY = "cs_demo_hMMtC_Jgtelh9shbyIjLQOC4USBeQJRCup46dCD_CLE"
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
const API_KEY = "your_key_here";
const HEADERS = { "Authorization": `Bearer ${API_KEY}`, "Content-Type": "application/json" };

const store = (chatId, message) =>
  fetch("https://api.chatsorter.com/process", {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({ chat_id: chatId, message })
  });

const retrieve = (chatId, query) =>
  fetch("https://api.chatsorter.com/search", {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({ chat_id: chatId, query })
  }).then(r => r.json());
```

---

## How It Works

Every message is scored for importance (1–10). Low-signal messages are buffered. Every 5 messages (configurable), a background summary is generated via local LLM inference. High-importance facts — names, allergies, preferences, relationships — are extracted into structured storage immediately and never lost across sessions.

At retrieval time, semantic similarity, importance score, and recency are combined into a composite score. You get back only what's relevant to the current query.

```
User message
     ↓
POST /process  →  Importance scoring  →  Buffer
                                              ↓ every N messages
                                         Background summary (local LLM)
                                              ↓
                                         Stored with embeddings + fact extraction
     ↓
POST /search   →  Semantic retrieval   →  Top memories returned
```

### Three-layer pipeline

**Layer 1 — Rolling buffer**
Messages accumulate in memory until N are collected (default: 5). The model never sees raw old messages — it sees compressed summaries.

**Layer 2 — Narrative summaries**
Every N messages get condensed into one coherent paragraph. Summaries are embedded and scored for importance. Old low-importance summaries decay over time; high-importance ones are permanent.

**Layer 3 — Structured fact extraction**
Facts are extracted per-message with confidence scoring and subject attribution. Facts about multiple people in a conversation are stored separately (`Sarah: nurse`, `Jake: has a dog named Max`). Conflicting facts are archived rather than overwritten — old values stay for audit, new values take precedence in retrieval.

---

## API Reference

### POST /process
Store a message and trigger background memory processing.

```json
{
  "chat_id": "user_123",
  "user_id": "user_123",
  "message": "I prefer vegetarian food",
  "role": "user",
  "session_date": "2026-09-11"
}
```

**Response:**
```json
{
  "success": true,
  "importance_score": 6.5,
  "message_count": 3,
  "facts": [{"type": "diet", "value": "vegetarian", "confidence": 0.88}]
}
```

### POST /search
Retrieve relevant memories for a query.

```json
{
  "chat_id": "user_123",
  "query": "what does this user eat",
  "max_memories": 8,
  "importance_threshold": 0.0
}
```

**Response:**
```json
{
  "success": true,
  "memories": [
    {"summary": "User prefers vegetarian food", "score": 0.94, "source": "structured"},
    {"summary": "User is allergic to peanuts and lives in Austin", "score": 0.87, "source": "summary"}
  ]
}
```

### POST /sdk/v1
One-call endpoint — store and retrieve in a single request.

```json
{
  "chat_id": "user_123",
  "user_id": "user_123",
  "message": "What restaurants do you recommend?",
  "retrieve_memories": true,
  "session_date": "2026-09-11"
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
  ],
  "messages_per_summary": 5
}
```

### GET /ingest/status/{job_id}
Poll bulk ingest progress.

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

Run ChatSorter entirely on your own infrastructure. Data never leaves your network. Suitable for healthcare, legal, and financial applications where conversation data cannot leave your infrastructure.

**Requirements:** Python 3.10+, [Ollama](https://ollama.ai)

```bash
git clone https://github.com/codeislife12/Chatsorter
cd Chatsorter
pip install -r requirements.txt
ollama pull gemma3:4b
ollama pull nomic-embed-text
python api.py
```

API runs on `localhost:5050`. No outbound calls for data processing — LLM inference runs entirely on your machine.

**Self-hosted commercial license:** free for personal use and under 10 end users. Contact for commercial licensing.

---

## Benchmark

Evaluated on [LoCoMo](https://github.com/snap-research/locomo) — 10 multi-session conversations, 1,540 questions across single-hop, multi-hop, temporal, and open-domain categories. Models: Gemma 3 12B (answer + judge), running locally via Ollama.

| | Score | Notes |
|--|-------|-------|
| GPT-4o, no memory layer | ~60% | Raw frontier model recall |
| ChatSorter + Gemma 3 12B | **61.5%** | Open-source, self-hosted, no API costs |

**Context hit rate: 99.4%** — ChatSorter retrieved relevant memory for nearly every question. Accuracy is bounded by the answer model's reasoning, not by retrieval.

**Failure breakdown (593 wrong answers):**

| Category | Count | % of total | Ceiling if fixed |
|----------|-------|------------|-----------------|
| idk_over_refusal | 279 | 18.1% | 80.3% |
| wrong_open_domain | 151 | 9.8% | 89.1% |
| wrong_single_hop | 72 | 4.7% | 93.8% |
| temporal_inference | 35 | 2.3% | 96.1% |
| wrong_date | 29 | 1.9% | 97.9% |
| no_context | 10 | 0.6% | 98.6% |

The dominant failure mode (18.1%) is model over-caution — the 12B model refusing to commit to an answer when it has the right context. This is a prompting problem, not a retrieval problem. Full methodology and results in [chatsorter_locomo_results/](chatsorter_locomo_results/).

---

## Pricing

| | Free | Starter | Growth | Enterprise |
|--|------|---------|--------|------------|
| End users | 10 | 500 | 5,000 | Unlimited |
| Memories | 1,000 | 50,000 | 500,000 | Unlimited |
| Hosting | Cloud | Cloud | Cloud | Self-hosted |
| Support | Community | Email | Priority | Dedicated |
| Price | $0 | $49/mo | $149/mo | Contact us |

---

## Stack

- **API:** Python, Flask, Waitress
- **LLM inference:** Ollama (gemma3:4b default, gemma3:12b recommended)
- **Embeddings:** nomic-embed-text
- **Storage:** Local JSON + FAISS vector index
- **Auth:** SQLite + Firebase

---

## License

MIT for personal use and under 10 end users.
Commercial license required for production deployments above 10 end users.
[Contact](mailto:chatsorter@gmail.com) for enterprise and self-hosted commercial licensing.

---

## Links

- **Website:** [chatsorter.com](https://chatsorter.com)
- **API:** [api.chatsorter.com](https://api.chatsorter.com)
- **Demo:** [chatsorter.com/demo](https://chatsorter.com/demo)
- **Changelog:** [chatsorter.com/changelog](https://chatsorter.com/changelog.html)
