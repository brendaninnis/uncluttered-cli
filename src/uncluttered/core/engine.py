"""Pipeline orchestrator for recipe search and extraction."""

from .agent import extract_recipe
from .database import add_recipe, create_tables, get_all_slugs
from .models import Recipe
from .search import search_for_recipes
from .utils import generate_slug, make_unique_slug


def process_query(
    query: str,
    fetch_count: int = 5,
    display_count: int = 3,
) -> list[Recipe]:
    """
    Orchestrate the full multi-recipe pipeline: Search -> Extract -> Save.

    Args:
        query: User's recipe search query (e.g., "Best Carbonara")
        fetch_count: Number of recipes to fetch and save (default 5)
        display_count: Number of top recipes to return for display (default 3)

    Returns:
        Top recipes sorted by trust score for display
    """
    # Ensure tables exist
    create_tables()

    # Step 1: Search for multiple recipe sources
    search_results = search_for_recipes(query, num_results=fetch_count)

    if not search_results:
        raise ValueError(f"No search results found for: {query}")

    # Get existing slugs to ensure uniqueness
    existing_slugs = get_all_slugs()

    # Step 2: Extract recipes from each source
    recipes: list[Recipe] = []
    errors: list[str] = []
    for result in search_results:
        try:
            # Build context from search result
            context = f"--- Source: {result.url} ---\nTitle: {result.title}\n\n{result.content}\n"

            # Extract structured recipe
            recipe = extract_recipe(context)

            # Generate unique slug
            base_slug = generate_slug(recipe.title)
            unique_slug = make_unique_slug(base_slug, existing_slugs)
            existing_slugs.add(unique_slug)

            # Add metadata
            recipe.slug = unique_slug
            recipe.search_term = query.lower()
            recipe.source_url = result.url

            # Save to database
            saved_recipe = add_recipe(recipe)
            recipes.append(saved_recipe)

        except Exception as e:
            errors.append(f"{result.url}: {e}")
            continue

    if not recipes:
        error_detail = "; ".join(errors[:3])
        raise ValueError(f"Failed to extract any recipes for: {query} ({error_detail})")

    # Step 3: Sort by trust score and return top N for display
    recipes.sort(
        key=lambda r: r.trust_score.score if r.trust_score else 0,
        reverse=True,
    )

    return recipes[:display_count]
