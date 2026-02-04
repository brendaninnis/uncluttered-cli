"""Recipe extraction agent using Google Gemini native structured output."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from .models import Recipe

load_dotenv()

# Lazy-loaded Gemini client
_client = None


def _get_client():
    """Get or create the Gemini client."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Get your key at: https://aistudio.google.com/apikey"
            )
        _client = genai.Client(api_key=api_key)
    return _client

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


def is_resource_exhausted(exception: BaseException) -> bool:
    """Check if the exception is a Gemini rate limit error."""
    if isinstance(exception, ClientError):
        if hasattr(exception, 'code') and exception.code == 429:
            return True
    if "RESOURCE_EXHAUSTED" in str(exception) or "429" in str(exception):
        return True
    return False


def log_retry(retry_state):
    """Log retry attempts to the console."""
    sleep_time = retry_state.next_action.sleep
    print(f"  Gemini is busy. Retrying in {sleep_time:.1f}s... (attempt {retry_state.attempt_number}/10)")


@retry(
    retry=retry_if_exception(is_resource_exhausted),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    stop=stop_after_attempt(10),
    before_sleep=log_retry,
)
def extract_recipe(context: str) -> Recipe:
    """
    Extract a structured Recipe from raw search context.

    Args:
        context: Raw text content from search results

    Returns:
        A validated Recipe object with trust score
    """
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"{SYSTEM_PROMPT}\n\nExtract a recipe from the following context:\n\n{context}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Recipe,
        ),
    )

    # Parse the JSON response into our Pydantic model
    recipe = Recipe.model_validate_json(response.text)

    return recipe
