# test_intent.py - Test improved intent detection and query extraction
from intent_detector import parse_web_intent

test_cases = [
    "What are the latest quantum computing breakthroughs? Check the web for recent developments.",
    "Tell me about SpaceX Starship. Search the web for updates.",
    "Go check web for AI safety research",
    "How does nuclear fusion work? Look online for explanations.",
    "Search web for climate change policies 2024",
    "What is quantum entanglement?",  # No web intent
]

print("Query Extraction Tests:\n")
print("="*80)

for text in test_cases:
    has_intent, query = parse_web_intent(text)
    print(f"\nInput: {text}")
    print(f"  Web Intent: {has_intent}")
    print(f"  Extracted Query: '{query}'")
    print("-"*80)
