# test_web_search.py - Test V3 web search functionality
from datetime import datetime, timezone
import uuid
from twistedtypes import Signal
from web_enrichment import enrich_signal_with_web

# Test Case 1: Web search intent
print("="*80)
print("TEST 1: Web Search Intent Detection")
print("="*80)

test_signal_1 = Signal(
    id=str(uuid.uuid4()),
    content="What are the latest quantum computing breakthroughs? Check the web for recent developments.",
    source="manual://test",
    captured_at=datetime.now(timezone.utc).isoformat(),
    tags=[],
    metadata={}
)

print(f"\nOriginal content:\n{test_signal_1.content}\n")

try:
    enriched_1 = enrich_signal_with_web(test_signal_1, max_results=2)
    print(f"Source: {enriched_1.source}")
    print(f"Tags: {enriched_1.tags}")
    print(f"Web enriched: {enriched_1.metadata.get('web_enriched', False)}")
    
    if enriched_1.metadata.get('web_sources'):
        print(f"\nWeb sources found:")
        for i, source in enumerate(enriched_1.metadata['web_sources'], 1):
            print(f"  {i}. {source['title']}")
            print(f"     {source['url']}")
    
    print(f"\nEnriched content preview (first 500 chars):")
    print(enriched_1.content[:500] + "...")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test Case 2: No web search intent
print("\n\n" + "="*80)
print("TEST 2: No Web Search Intent")
print("="*80)

test_signal_2 = Signal(
    id=str(uuid.uuid4()),
    content="Explain quantum entanglement in simple terms.",
    source="manual://test",
    captured_at=datetime.now(timezone.utc).isoformat(),
    tags=[],
    metadata={}
)

print(f"\nOriginal content:\n{test_signal_2.content}\n")

try:
    enriched_2 = enrich_signal_with_web(test_signal_2)
    print(f"Web enriched: {enriched_2.metadata.get('web_enriched', False)}")
    print(f"Content unchanged: {enriched_2.content == test_signal_2.content}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*80)
print("Tests complete!")
print("="*80)
