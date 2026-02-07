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

## Trust Score Rubric

You must also assign a Trust Score (0-100) based on the quality of the recipe:

**Base Score: 50 points**

**Additions:**
- +20 points: Exact measurements are used (grams, ounces, cups with precise amounts)
- +10 points: Source is a known culinary authority (Serious Eats, NYT Cooking,
  Bon Appetit, America's Test Kitchen, Food Network, Epicurious, Allrecipes)
- +10 points: Clear, detailed instructions with timing cues
- +5 points: Includes both prep time and cook time
- +5 points: Specifies exact yield/servings

**Deductions:**
- -20 points: Vague ingredient amounts ("some", "a bit", "to taste" for main ingredients)
- -15 points: Missing critical steps or unclear instructions
- -10 points: No source attribution or unknown blog
- -5 points: Missing timing information

Provide clear reasoning for your Trust Score calculation.
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
