"""
web_search.py — DuckDuckGo-powered web search service.

This module provides real-time web search without any API key.
Results are injected as context into the LLM to produce grounded answers.
"""

import re
import httpx
from typing import Optional


def search(query: str, max_results: int = 4) -> list[dict]:
    """
    Perform a DuckDuckGo text search and return the top results.

    Returns:
        A list of dicts: [{title, url, snippet}, ...]
        Returns an empty list if search fails or library is unavailable.
    """
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title":   r.get("title", ""),
                    "url":     r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
        return results
    except ImportError:
        print("⚠️  duckduckgo-search not installed. Run: pip install duckduckgo-search")
        return []
    except Exception as e:
        print(f"⚠️  Web search failed: {e}")
        return []


async def fetch_url_content(url: str, max_chars: int = 4000) -> Optional[str]:
    """
    Fetch and extract plain text from a URL.

    Strips HTML tags and returns up to max_chars characters of content.
    Returns None if the request fails.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            html = resp.text

        # Very lightweight HTML-to-text: strip tags and collapse whitespace
        text = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text[:max_chars]
    except Exception as e:
        print(f"⚠️  URL fetch failed for {url}: {e}")
        return None


def build_web_context(results: list[dict]) -> str:
    """
    Format search results into a context block for the LLM prompt.
    """
    if not results:
        return ""

    parts = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"[Web Result {i}] {r['title']}\n"
            f"URL: {r['url']}\n"
            f"{r['snippet']}"
        )
    return "\n\n---\n\n".join(parts)
