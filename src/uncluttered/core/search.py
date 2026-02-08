"""Search service using Tavily API."""

import os
from dataclasses import dataclass

from tavily import TavilyClient


@dataclass
class SearchResult:
    """A single search result from Tavily."""

    url: str
    title: str
    content: str
    score: float = 0.0


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
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY environment variable is required. Get your key at: https://tavily.com"
        )
    client = TavilyClient(api_key=api_key)

    excluded = set(exclude_urls) if exclude_urls else set()
    max_results = min(num_results + len(excluded), 20)

    response = client.search(
        query=f"{query} recipe ingredients instructions",
        search_depth="advanced",
        max_results=max_results,
        include_raw_content=True,
    )

    results = []
    for result in response.get("results", []):
        url = result.get("url", "")
        title = result.get("title", "Untitled")
        raw_content = result.get("raw_content", "")
        content = result.get("content", "")
        relevance = result.get("score", 0.0)

        # Prefer raw_content if available
        text = raw_content if raw_content else content

        if text and url and url not in excluded:
            results.append(SearchResult(url=url, title=title, content=text, score=relevance))

    return results[:num_results]
