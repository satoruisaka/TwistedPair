# test_ddgs.py - Quick test of DuckDuckGo search
print("Testing DuckDuckGo search...\n")

try:
    # Try new package name
    try:
        from ddgs import DDGS
        print("✓ Using 'ddgs' package (new name)")
    except ImportError:
        from duckduckgo_search import DDGS
        print("✓ Using 'duckduckgo_search' package (old name)")
    
    query = "Python programming"
    print(f"Searching for: {query}\n")
    
    ddgs = DDGS()
    results = list(ddgs.text(query, max_results=3))
    
    print(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.get('title', 'No title')}")
        print(f"   URL: {result.get('href', 'No URL')}")
        print(f"   Snippet: {result.get('body', 'No snippet')[:100]}...")
        print()
    
    if len(results) == 0:
        print("WARNING: Search returned 0 results. Possible causes:")
        print("  - DuckDuckGo rate limiting")
        print("  - Network connectivity issue")
        print("  - Library version incompatibility")
        print("\nTry: pip install --upgrade ddgs")
    
except ImportError as e:
    print(f"ERROR: DuckDuckGo library not installed")
    print(f"Install with: pip install ddgs")
    print(f"Details: {e}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
