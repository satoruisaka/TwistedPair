# web_search.py - Web search using Brave Search API (primary) and DuckDuckGo (fallback)
from typing import List, Dict, Optional
import logging
import os
import requests

logger = logging.getLogger(__name__)


class SearchResult:
    """Single search result with title, snippet, and URL."""
    def __init__(self, title: str, snippet: str, url: str):
        self.title = title
        self.snippet = snippet
        self.url = url
    
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "snippet": self.snippet,
            "url": self.url
        }


def search_brave(query: str, max_results: int = 7) -> List[SearchResult]:
    """
    Search the web using Brave Search API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 7)
        
    Returns:
        List of SearchResult objects
        
    Raises:
        Exception: If search fails or API key not configured
    """
    # Try environment variable first, then config.py
    api_key = os.environ.get('BRAVE_API_KEY')
    if not api_key:
        try:
            from config import BRAVE_API_KEY
            api_key = BRAVE_API_KEY
        except ImportError:
            pass
    
    if not api_key:
        raise Exception("BRAVE_API_KEY not found in environment or config.py")
    
    try:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }
        
        params = {
            "q": query,
            "count": max_results
        }
        
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('web', {}).get('results', []):
            results.append(SearchResult(
                title=item.get('title', 'No title'),
                snippet=item.get('description', 'No snippet'),
                url=item.get('url', '')
            ))
        
        logger.info(f"Brave API: Found {len(results)} results for query: {query}")
        return results
        
    except requests.RequestException as e:
        logger.error(f"Brave API request failed: {str(e)}")
        raise Exception(f"Brave API failed: {str(e)}")
    except Exception as e:
        logger.error(f"Brave API error: {str(e)}")
        raise Exception(f"Brave API error: {str(e)}")


def search_duckduckgo(query: str, max_results: int = 7) -> List[SearchResult]:
    """
    Search the web using DuckDuckGo (fallback).
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 7)
        
    Returns:
        List of SearchResult objects
        
    Raises:
        Exception: If search fails
    """
    try:
        from ddgs import DDGS
        
        results = []
        ddgs = DDGS()
        search_results = list(ddgs.text(query, max_results=max_results))
        
        for result in search_results:
            results.append(SearchResult(
                title=result.get('title', 'No title'),
                snippet=result.get('body', 'No snippet'),
                url=result.get('href', '')
            ))
        
        logger.info(f"DuckDuckGo: Found {len(results)} results for query: {query}")
        return results
        
    except ImportError:
        logger.error("ddgs not installed. Install with: pip install ddgs")
        raise Exception("Web search library not installed. Run: pip install ddgs")
    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {str(e)}")
        raise Exception(f"DuckDuckGo search failed: {str(e)}")


def search_web(query: str, max_results: int = 7) -> List[SearchResult]:
    """
    Search the web using Brave API (primary) with DuckDuckGo fallback.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 7)
        
    Returns:
        List of SearchResult objects
        
    Raises:
        Exception: If both search methods fail
    """
    # Try Brave first
    try:
        return search_brave(query, max_results)
    except Exception as brave_error:
        logger.warning(f"Brave API failed, falling back to DuckDuckGo: {str(brave_error)}")
        
        # Fallback to DuckDuckGo
        try:
            return search_duckduckgo(query, max_results)
        except Exception as ddg_error:
            logger.error(f"Both search methods failed. Brave: {brave_error}, DuckDuckGo: {ddg_error}")
            raise Exception(f"All search methods failed. Try: 1) Set BRAVE_API_KEY, 2) Install ddgs")


if __name__ == "__main__":
    # Test search
    import sys
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "quantum computing breakthroughs 2024"
    
    print(f"Searching for: {query}\n")
    
    try:
        results = search_web(query, max_results=3)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title}")
            print(f"   {result.snippet[:100]}...")
            print(f"   {result.url}")
            print()
    except Exception as e:
        print(f"Error: {e}")
