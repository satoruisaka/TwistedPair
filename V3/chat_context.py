"""
Chat context builder for TwistedPair V2.

Formats conversation history into LLM prompts while respecting context limits.
"""

from typing import List
import sys
from pathlib import Path

# Import parent directory types
sys.path.insert(0, str(Path(__file__).parent.parent))
from pedal import distort
from twistedtypes import Signal, Knobs, Prompt

from session_manager import ChatSession, ChatMessage


def estimate_token_count(text: str) -> int:
    """
    Rough estimate of token count (1 token ≈ 4 characters for English text).
    This is conservative - actual tokenization varies by model.
    """
    return len(text) // 4


def build_chat_prompt(session: ChatSession, new_user_message: str) -> Prompt:
    """
    Build an LLM prompt from chat session history + new message.
    
    Strategy:
    1. Start with system prompt from distort() (mode + tone instructions)
    2. Add conversation history as context
    3. Append new user message
    4. Truncate older messages if exceeding context limit (32K tokens ≈ 128K chars)
    
    Args:
        session: Active chat session with history
        new_user_message: Latest user input
    
    Returns:
        Prompt ready for Agent.run()
    """
    # Get base system prompt from pedal (mode + tone instructions)
    # Create a minimal Signal just to get the system prompt
    dummy_signal = Signal(
        id="chat-context",
        content=new_user_message,
        source="chat",
        captured_at="",
        tags=[],
        metadata={}
    )
    base_prompt = distort(dummy_signal, session.knobs)
    
    # Build conversation context
    conversation_lines = []
    
    # Add previous messages in chronological order
    for msg in session.messages:
        if msg.role == "user":
            conversation_lines.append(f"User: {msg.content}")
        else:  # assistant
            conversation_lines.append(f"Assistant: {msg.content}")
    
    # Add new user message
    conversation_lines.append(f"User: {new_user_message}")
    
    conversation_text = "\n\n".join(conversation_lines)
    
    # Check token count and truncate if needed
    MAX_CONTEXT_TOKENS = 30000  # Leave room for system prompt + response (32K total)
    estimated_tokens = estimate_token_count(base_prompt.system + conversation_text)
    
    if estimated_tokens > MAX_CONTEXT_TOKENS:
        # Truncate from the beginning (oldest messages)
        conversation_text = _truncate_conversation(
            conversation_lines,
            base_prompt.system,
            MAX_CONTEXT_TOKENS
        )
    
    # Build final user prompt with conversation history
    user_prompt = f"""Previous conversation:

{conversation_text}

Continue the conversation by responding to the most recent user message. Maintain consistency with the conversation history and your assigned rhetorical mode."""
    
    return Prompt(
        system=base_prompt.system,
        user=user_prompt,
        temperature=base_prompt.temperature,
        top_k=base_prompt.top_k,
        top_p=base_prompt.top_p,
        metadata={"session_id": session.session_id, "turn_count": len(session.messages)}
    )


def _truncate_conversation(
    conversation_lines: List[str],
    system_prompt: str,
    max_tokens: int
) -> str:
    """
    Truncate conversation from the beginning while keeping recent messages.
    Always keeps the last user message and at least 2-3 turns of context.
    """
    system_tokens = estimate_token_count(system_prompt)
    available_tokens = max_tokens - system_tokens
    
    # Always keep last 3 turns (6 messages if alternating user/assistant)
    min_keep = min(6, len(conversation_lines))
    
    # Work backwards from most recent messages
    kept_lines = []
    current_tokens = 0
    
    for line in reversed(conversation_lines):
        line_tokens = estimate_token_count(line)
        
        if current_tokens + line_tokens > available_tokens and len(kept_lines) >= min_keep:
            break
        
        kept_lines.insert(0, line)
        current_tokens += line_tokens
    
    # Add truncation notice if we dropped messages
    if len(kept_lines) < len(conversation_lines):
        truncated_count = len(conversation_lines) - len(kept_lines)
        notice = f"[... {truncated_count} earlier messages truncated for context limit ...]"
        kept_lines.insert(0, notice)
    
    return "\n\n".join(kept_lines)


def format_history_for_display(session: ChatSession) -> List[dict]:
    """
    Format conversation history for frontend display.
    
    Returns list of message objects with role, content, timestamp.
    """
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp
        }
        for msg in session.messages
    ]
