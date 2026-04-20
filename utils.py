"""
Utility functions for the Software Engineering Assistant.
Handles chat export, token estimation, and input validation.
"""

import json
from datetime import datetime


def estimate_tokens(text: str) -> int:
    """
    Rough token estimation based on word count.
    Approximation: 1 token ~ 0.75 words for English text.
    """
    words = len(text.split())
    return int(words / 0.75)


def export_chat_as_markdown(chat_history: list) -> str:
    """
    Export the conversation history as a clean markdown document.
    """
    lines = [
        f"# Chat Export",
        f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
    ]

    for msg in chat_history:
        role = msg.__class__.__name__.replace("Message", "")
        prefix = "You" if role == "Human" else "Assistant"
        lines.append(f"### {prefix}")
        lines.append(msg.content)
        lines.append("")

    return "\n".join(lines)


def export_chat_as_json(chat_history: list) -> str:
    """
    Export the conversation history as JSON.
    """
    messages = []
    for msg in chat_history:
        role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
        messages.append({"role": role, "content": msg.content})

    return json.dumps({
        "exported_at": datetime.now().isoformat(),
        "messages": messages
    }, indent=2)


def validate_input(text: str) -> tuple[bool, str]:
    """
    Basic input validation.
    Returns (is_valid, error_message).
    """
    if not text or not text.strip():
        return False, "Please enter a message."

    if len(text) > 10000:
        return False, "Message is too long. Please keep it under 10,000 characters."

    return True, ""
