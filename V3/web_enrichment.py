# web_enrichment.py - Enrich signals with web search results
from typing import Optional
import logging
from twistedtypes import Signal
from intent_detector import parse_web_intent
from web_search import search_web
from web_fetcher import fetch_multiple_urls

logger = logging.getLogger(__name__)


def enrich_signal_with_web(signal: Signal, max_results: int = 7) -> Signal:
    """
    Enrich a signal with web search results if web search intent detected.
    
    Args:
        signal: Original signal from user
        max_results: Maximum number of search results to fetch (default 7)
        
    Returns:
        Enriched signal with web content appended, or original if no web intent
    """
    # Check for web search intent
    has_intent, query = parse_web_intent(signal.content)
    
    if not has_intent or not query:
        logger.info("No web search intent detected")
        return signal
    
    logger.info(f"Web search intent detected: '{query}'")
    
    try:
        # Search the web
        search_results = search_web(query, max_results=max_results)
        
        if not search_results:
            logger.warning("No search results found")
            return signal
        
        # Fetch content from URLs
        urls = [result.url for result in search_results]
        fetched_contents = fetch_multiple_urls(urls, max_chars_per_url=10000)
        
        if not fetched_contents:
            logger.warning("Failed to fetch any content")
            return signal
        
        # Build enriched content with snippets always shown
        enriched_content = f"{signal.content}\n\n{'='*80}\n"
        enriched_content += f"WEB SEARCH RESULTS FOR: {query}\n"
        enriched_content += f"{'='*80}\n\n"
        
        # Create lookup for fetched content by URL
        fetched_by_url = {content.url: content for content in fetched_contents}
        
        web_sources = []
        for i, search_result in enumerate(search_results, 1):
            # Always show snippet
            enriched_content += f"[SOURCE {i}] {search_result.title}\n"
            enriched_content += f"URL: {search_result.url}\n"
            enriched_content += f"Snippet: {search_result.snippet}\n"
            enriched_content += f"{'-'*80}\n"
            
            # Append full content if successfully fetched
            if search_result.url in fetched_by_url:
                content = fetched_by_url[search_result.url]
                enriched_content += f"Full Content:\n{content.text}\n\n"
                status = "fetched"
            else:
                enriched_content += f"[Full content unavailable - site blocked or failed to fetch]\n\n"
                status = "snippet_only"
            
            # Extract domain from URL
            from urllib.parse import urlparse
            domain = urlparse(search_result.url).netloc
            
            web_sources.append({
                "title": search_result.title,
                "url": search_result.url,
                "domain": domain,
                "snippet": search_result.snippet,
                "status": status
            })
        
        # Update signal metadata
        updated_metadata = signal.metadata.copy()
        updated_metadata['web_search_query'] = query
        updated_metadata['web_sources'] = web_sources
        updated_metadata['web_enriched'] = True
        
        # Create enriched signal
        enriched_signal = Signal(
            id=signal.id,
            content=enriched_content,
            source=f"web://{query}",
            captured_at=signal.captured_at,
            tags=signal.tags + ['web_search'],
            metadata=updated_metadata
        )
        
        logger.info(f"Signal enriched with {len(fetched_contents)} web sources")
        return enriched_signal
        
    except Exception as e:
        logger.error(f"Web enrichment failed: {str(e)}")
        # Return original signal on error
        return signal


if __name__ == "__main__":
    # Test web enrichment
    from datetime import datetime, timezone
    import uuid
    
    test_signal = Signal(
        id=str(uuid.uuid4()),
        content="What are the latest breakthroughs in quantum computing? Check the web for recent developments.",
        source="manual://test",
        captured_at=datetime.now(timezone.utc).isoformat(),
        tags=[],
        metadata={}
    )
    
    print("Original Signal:")
    print(f"Content: {test_signal.content}\n")
    
    enriched = enrich_signal_with_web(test_signal, max_results=2)
    
    print("\nEnriched Signal:")
    print(f"Source: {enriched.source}")
    print(f"Tags: {enriched.tags}")
    print(f"Web Sources: {enriched.metadata.get('web_sources', [])}")
    print(f"\nContent (first 1000 chars):\n{enriched.content[:1000]}...")
