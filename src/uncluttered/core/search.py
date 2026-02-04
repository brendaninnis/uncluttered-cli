"""Search service using Tavily API."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


@dataclass
class SearchResult:
    """A single search result from Tavily."""
    url: str
    title: str
    content: str


def search_for_recipes(query: str, num_results: int = 5) -> list[SearchResult]:
    """
    Search for recipe sources using Tavily API.

    Args:
        query: The search query (e.g., "Best Carbonara recipe")
        num_results: Number of results to return (default 5)

    Returns:
        List of SearchResult objects with URL, title, and content.
    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    response = client.search(
        query=f"{query} recipe ingredients instructions",
        search_depth="advanced",
        max_results=num_results,
        include_raw_content=True,
    )

    results = []
    for result in response.get("results", []):
        url = result.get("url", "")
        title = result.get("title", "Untitled")
        raw_content = result.get("raw_content", "")
        content = result.get("content", "")

        # Prefer raw_content if available
        text = raw_content if raw_content else content

        if text and url:
            results.append(SearchResult(url=url, title=title, content=text))

    return results


def search_for_context(query: str) -> str:
    """
    Search for recipe information using Tavily API.

    Args:
        query: The search query (e.g., "Best Carbonara recipe")

    Returns:
        Concatenated content from top 3 search results.
    """
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # Search with recipe-focused query
    response = client.search(
        query=f"{query} recipe ingredients instructions",
        search_depth="advanced",
        max_results=3,
        include_raw_content=True,
    )

    # Concatenate content from top results
    context_parts = []
    for result in response.get("results", []):
        source = result.get("url", "Unknown source")
        title = result.get("title", "Untitled")
        content = result.get("content", "")
        raw_content = result.get("raw_content", "")

        # Prefer raw_content if available, otherwise use content
        text = raw_content if raw_content else content

        if text:
            context_parts.append(
                f"--- Source: {source} ---\n"
                f"Title: {title}\n\n"
                f"{text}\n"
            )

    return "\n\n".join(context_parts)
