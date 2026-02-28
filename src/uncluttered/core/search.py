"""Search service using Tavily API."""

import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from tavily import TavilyClient

# Domains that rarely contain extractable recipe text (video/social platforms).
# URLs matching these are filtered out before LLM extraction to save cost.
EXCLUDED_DOMAINS = {
    "youtube.com",
    "youtu.be",
    "tiktok.com",
    "instagram.com",
    "facebook.com",
    "pinterest.com",
}

# Cached client (singleton)
_tavily_client: TavilyClient | None = None


def _get_tavily_client() -> TavilyClient:
    """Get or create the cached TavilyClient."""
    global _tavily_client
    if _tavily_client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY environment variable is required. Get your key at: https://tavily.com"
            )
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client


@dataclass
class SearchResult:
    """A single search result from Tavily."""

    url: str
    title: str
    content: str
    score: float = 0.0


def _clean_content(text: str) -> str:
    """Strip URLs, collapse whitespace, and cap length to reduce LLM input bloat."""
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text[:40_000]


def search_for_recipes(
    query: str,
    num_results: int = 5,
    exclude_urls: list[str] | None = None,
) -> list[SearchResult]:
    """
    Search for recipe sources using Tavily API.

    Args:
        query: The search query (e.g., "Best Carbonara recipe")
        num_results: Number of results to return (default 5)
        exclude_urls: URLs to exclude from results (e.g., already-saved recipes)

    Returns:
        List of SearchResult objects with URL, title, and content.
    """
    client = _get_tavily_client()
    excluded = set(exclude_urls) if exclude_urls else set()

    # Extract domains from excluded URLs so Tavily never returns results
    # from sites the user already has recipes from.
    exclude_domains = list(
        {(urlparse(u).hostname or "").removeprefix("www.").removeprefix("m.") for u in excluded}
        - {""}
    )

    response = client.search(
        query=f"{query} recipe ingredients instructions",
        search_depth="basic",
        max_results=min(num_results + 3, 20),
        include_raw_content=True,
        exclude_domains=exclude_domains if exclude_domains else None,
    )

    results = []
    for result in response.get("results", []):
        url = result.get("url", "")
        title = result.get("title", "Untitled")
        raw_content = result.get("raw_content", "")
        content = result.get("content", "")
        relevance = result.get("score", 0.0)

        # Prefer raw_content if available, then clean for LLM extraction
        text = _clean_content(raw_content if raw_content else content)

        # Strip www./m. prefixes to match against EXCLUDED_DOMAINS
        domain = urlparse(url).hostname or ""
        domain = domain.removeprefix("www.").removeprefix("m.")

        if text and url and url not in excluded and domain not in EXCLUDED_DOMAINS:
            results.append(SearchResult(url=url, title=title, content=text, score=relevance))

    return results[:num_results]
