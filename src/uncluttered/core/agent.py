"""Recipe extraction agent with pluggable LLM providers."""

from .models import Recipe
from .providers import get_provider

SYSTEM_PROMPT = """You are a recipe extraction expert. Your job is to extract a complete,
well-structured recipe from the provided context.

Extract the following information:
- Title: The name of the dish
- Description: A brief 1-2 sentence description
- Ingredients: Each ingredient with quantity, unit, and name
- Instructions: Step-by-step cooking instructions
- Prep time and cook time (if mentioned)
- Yield/servings (use the field name "serving_yield")

## Trust Score

Assign a Trust Score (0-100) reflecting how much you'd trust this recipe to produce a good
result if followed by a competent home cook. Use your judgment — assess the recipe holistically
rather than checking boxes.

Things worth considering:
- **Precision**: Are measurements specific and reproducible? Grams or exact cup amounts are
  more trustworthy than "a handful" or "some".
- **Completeness**: Are the instructions detailed enough to follow without guessing? Look for
  temperatures, timing cues, and technique.
- **Credibility**: Does the source seem knowledgeable? Do the techniques and ratios make
  culinary sense for this type of dish?

Search metadata (source URL, search rank, relevance score) is provided for context. A high
search rank or well-known source may be a positive signal, but the recipe content itself
matters most.

For calibration:
- 85-100: Exceptional — precise, well-tested, from a credible source, you'd recommend it
- 65-84: Solid — clear and complete with minor gaps
- 45-64: Adequate — functional but vague in places or missing useful detail
- Below 45: Unreliable — significant gaps, unclear instructions, or questionable techniques

Provide brief reasoning explaining your assessment.
"""


def extract_recipe(context: str) -> Recipe:
    """Extract a structured Recipe from raw search context.

    Args:
        context: Raw text content from search results

    Returns:
        A validated Recipe object with trust score
    """
    provider = get_provider()
    return provider.extract_recipe(
        SYSTEM_PROMPT,
        f"Extract a recipe from the following context:\n\n{context}",
    )
