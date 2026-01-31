# web_fetcher.py - Fetch and extract content from URLs
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import logging
import random
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Import user agents from config
try:
    from config import USER_AGENTS
except ImportError:
    # Fallback if config not available
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]


def get_random_user_agent() -> str:
    """Get a random user agent from the pool."""
    return random.choice(USER_AGENTS)


class FetchedContent:
    """Container for fetched web content."""
    def __init__(self, url: str, title: str, text: str, metadata: dict):
        self.url = url
        self.title = title
        self.text = text
        self.metadata = metadata
    
    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "text": self.text,
            "metadata": self.metadata
        }


def fetch_url(url: str, max_chars: int = 30000) -> FetchedContent:
    """
    Fetch content from a URL and extract clean text.
    
    Args:
        url: URL to fetch
        max_chars: Maximum characters to extract (default 30K to fit in 32K context)
        
    Returns:
        FetchedContent object with extracted text and metadata
        
    Raises:
        Exception: If fetch or parsing fails
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")
        
        # Fetch with timeout and rotating user agent
        headers = {"User-Agent": get_random_user_agent()}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else parsed.netloc
        
        # Remove script, style, and navigation elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Extract text from main content areas (prioritize)
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
        else:
            # Fallback to body
            text = soup.get_text(separator='\n', strip=True)
        
        # Clean up text: remove excessive newlines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        # Truncate if too long
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Content truncated...]"
        
        metadata = {
            "domain": parsed.netloc,
            "content_type": response.headers.get('Content-Type', 'unknown'),
            "length": len(text)
        }
        
        logger.info(f"Fetched {len(text)} chars from {url}")
        return FetchedContent(url, title, text, metadata)
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {str(e)}")
        raise Exception(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing {url}: {str(e)}")
        raise Exception(f"Error processing URL: {str(e)}")


def fetch_multiple_urls(urls: list[str], max_chars_per_url: int = 10000) -> list[FetchedContent]:
    """
    Fetch content from multiple URLs.
    
    Args:
        urls: List of URLs to fetch
        max_chars_per_url: Maximum characters per URL (default 10K to fit multiple in context)
        
    Returns:
        List of FetchedContent objects (excludes failed fetches)
    """
    results = []
    for url in urls:
        try:
            content = fetch_url(url, max_chars=max_chars_per_url)
            results.append(content)
        except Exception as e:
            logger.warning(f"Skipping {url}: {str(e)}")
            continue
    
    return results


if __name__ == "__main__":
    # Test fetching
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://en.wikipedia.org/wiki/Quantum_computing"
    
    print(f"Fetching: {url}\n")
    
    try:
        content = fetch_url(url)
        print(f"Title: {content.title}")
        print(f"Domain: {content.metadata['domain']}")
        print(f"Length: {content.metadata['length']} chars")
        print(f"\nFirst 500 chars:\n{content.text[:500]}...")
    except Exception as e:
        print(f"Error: {e}")
