"""
ChatSorter — System Prompt Injection Example
Shows how to inject retrieved memories into your LLM system prompt
so your bot actually uses what it remembers.

Get a free API key at: chatsorter-website.vercel.app
"""

import requests

API_KEY  = "your_api_key_here"
BASE_URL = "https://your-chatsorter-url.com"
HEADERS  = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


def get_memories(chat_id: str, user_id: str, message: str) -> list:
    resp = requests.post(f"{BASE_URL}/chat", json={
        "chat_id": chat_id,
        "user_id": user_id,
        "message": message
    }, headers=HEADERS)
    return resp.json().get("retrieved_memories", [])


def build_system_prompt(memories: list, base_prompt: str = None) -> str:
    """
    Inject ChatSorter memories into your system prompt.
    Pass this as the system message to any LLM (OpenAI, Anthropic, etc).
    """
    base = base_prompt or "You are a helpful, friendly assistant."

    if not memories:
        return base

    # Sort by importance so the most critical facts come first
    sorted_memories = sorted(memories, key=lambda m: m.get("importance_score", 0), reverse=True)
    memory_lines    = "\n".join([f"- {m['summary']}" for m in sorted_memories])

    return f"""{base}

What you remember about this user from previous conversations:
{memory_lines}

Use this context naturally. Do not repeat it back word for word.
If the user asks something you have context for, use it."""


# ── Example with OpenAI ──────────────────────────────────────────────────────

def chat_with_openai(user_message: str, chat_id: str, user_id: str):
    """Full example using OpenAI + ChatSorter memory injection."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key="your_openai_key")
    except ImportError:
        print("pip install openai")
        return

    memories      = get_memories(chat_id, user_id, user_message)
    system_prompt = build_system_prompt(memories)

    print(f"[DEBUG] Injecting {len(memories)} memories into system prompt")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",  "content": system_prompt},
            {"role": "user",    "content": user_message}
        ]
    )
    return response.choices[0].message.content


# ── Example with Anthropic ───────────────────────────────────────────────────

def chat_with_anthropic(user_message: str, chat_id: str, user_id: str):
    """Full example using Anthropic Claude + ChatSorter memory injection."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key="your_anthropic_key")
    except ImportError:
        print("pip install anthropic")
        return

    memories      = get_memories(chat_id, user_id, user_message)
    system_prompt = build_system_prompt(memories)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text


if __name__ == "__main__":
    # Standalone test — just prints the system prompt that would be generated
    sample_memories = [
        {"summary": "Alice is 28 and lives in Seattle.", "importance_score": 7.5, "source": "summary"},
        {"summary": "Alice is allergic to peanuts and shellfish.", "importance_score": 9.5, "source": "master"},
        {"summary": "Alice works as a software engineer and has a dog named Max.", "importance_score": 8.0, "source": "master"},
    ]

    prompt = build_system_prompt(sample_memories)
    print("Generated system prompt:")
    print("─" * 60)
    print(prompt)
