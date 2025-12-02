# intent_detector.py - Natural language intent detection for web search
import re
from typing import Optional, Tuple


# Patterns that trigger web search
WEB_SEARCH_PATTERNS = [
    r'\b(?:check|search|look)\s+(?:the\s+)?web\b',
    r'\b(?:search|look)\s+online\b',
    r'\bfind\s+(?:on\s+)?(?:the\s+)?(?:web|internet)\b',
    r'\bweb\s+search\b',
    r'\bcheck\s+online\b',
    r'\blook\s+up\s+online\b',
    r'\bsearch\s+for\s+(?:me\s+)?online\b',
    r'\bgo\s+(?:check|search|look)\s+(?:the\s+)?web\b',
]

# Compile patterns for performance
COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in WEB_SEARCH_PATTERNS]


def detect_web_search_intent(text: str) -> bool:
    """
    Detect if user text contains web search intent.
    
    Args:
        text: User input text
        
    Returns:
        True if web search intent detected, False otherwise
    """
    for pattern in COMPILED_PATTERNS:
        if pattern.search(text):
            return True
    return False


def extract_search_query(text: str) -> Optional[str]:
    """
    Extract search query from user text with web search intent.
    
    Strategies:
    1. Extract the main question/topic before the trigger phrase
    2. Look for explicit "for/about X" after trigger phrase
    3. Remove trigger phrases and use remaining text as query
    
    Args:
        text: User input text with web search intent
        
    Returns:
        Extracted search query or None if can't extract
    """
    if not detect_web_search_intent(text):
        return None
    
    # Strategy 1: Extract question before trigger phrase (preferred)
    # Patterns: "What/How/Why/When... ? Check web" or "Topic question. Check web"
    trigger_split = re.split(
        r'\b(?:check|search|look|find|go).*?\b(?:web|online|internet)\b',
        text,
        maxsplit=1,
        flags=re.IGNORECASE
    )
    if len(trigger_split) > 0 and trigger_split[0].strip():
        query = trigger_split[0].strip()
        # Remove trailing punctuation
        query = re.sub(r'[?.!,]+$', '', query).strip()
        if len(query) > 10:  # Reasonable question length
            return query
    
    # Strategy 2: Look for explicit "for/about X" after trigger phrase
    for_pattern = re.compile(
        r'(?:check|search|look|find).*?(?:for|about|on)\s+(.+?)(?:\.|$)',
        re.IGNORECASE | re.DOTALL
    )
    match = for_pattern.search(text)
    if match:
        query = match.group(1).strip()
        # Clean up common trailing phrases
        query = re.sub(r'\s*(?:please|thanks?|thank you)\s*$', '', query, flags=re.IGNORECASE)
        if query and len(query) > 3:
            return query
    
    # Strategy 3: Remove trigger phrases and use what's left
    cleaned = text
    for pattern in COMPILED_PATTERNS:
        cleaned = pattern.sub('', cleaned)
    
    # Clean up extra whitespace and punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = re.sub(r'^[,\.\?!\s]+|[,\.\?!\s]+$', '', cleaned)
    
    if cleaned and len(cleaned) > 3:
        return cleaned
    
    # Strategy 4: Fallback to full text (remove just the trigger word)
    fallback = re.sub(r'\b(?:check|search|look|find|go)\b', '', text, flags=re.IGNORECASE)
    fallback = re.sub(r'\b(?:web|online|internet|the)\b', '', fallback, flags=re.IGNORECASE)
    fallback = re.sub(r'\s+', ' ', fallback).strip()
    
    return fallback if fallback else text


def parse_web_intent(text: str) -> Tuple[bool, Optional[str]]:
    """
    Convenience function that both detects intent and extracts query.
    
    Args:
        text: User input text
        
    Returns:
        Tuple of (has_web_intent, search_query)
    """
    has_intent = detect_web_search_intent(text)
    query = extract_search_query(text) if has_intent else None
    return has_intent, query


if __name__ == "__main__":
    # Test cases
    test_inputs = [
        "What are quantum computing breakthroughs in 2024? Check the web for recent articles",
        "Go search the web for SpaceX Starship updates",
        "Tell me about AI safety research. Look online for recent papers",
        "Search web for climate change policies",
        "Find on the internet the latest news about fusion energy",
        "What is the capital of France?",  # No web intent
        "Explain quantum entanglement",  # No web intent
    ]
    
    print("Intent Detection Tests:\n")
    for text in test_inputs:
        has_intent, query = parse_web_intent(text)
        print(f"Input: {text}")
        print(f"  Web Intent: {has_intent}")
        print(f"  Query: {query}")
        print()
