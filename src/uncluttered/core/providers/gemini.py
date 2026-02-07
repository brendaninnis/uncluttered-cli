"""Google Gemini recipe provider."""

import os

from google import genai
from google.genai import types
from google.genai.errors import ClientError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from ..models import Recipe
from .base import RecipeProvider


def _is_resource_exhausted(exception: BaseException) -> bool:
    """Check if the exception is a Gemini rate limit error."""
    if isinstance(exception, ClientError):
        if hasattr(exception, "code") and exception.code == 429:
            return True
    if "RESOURCE_EXHAUSTED" in str(exception) or "429" in str(exception):
        return True
    return False


def _log_retry(retry_state):
    """Log retry attempts to the console."""
    sleep_time = retry_state.next_action.sleep
    print(
        f"  Gemini is busy. Retrying in {sleep_time:.1f}s... "
        f"(attempt {retry_state.attempt_number}/10)"
    )


class GeminiProvider(RecipeProvider):
    """Recipe extraction using Google Gemini."""

    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(self, model: str | None = None):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Get your key at: https://aistudio.google.com/apikey"
            )
        self._client = genai.Client(api_key=api_key)
        self._model = model or self.DEFAULT_MODEL

    @retry(
        retry=retry_if_exception(_is_resource_exhausted),
        wait=wait_exponential(multiplier=2, min=2, max=60),
        stop=stop_after_attempt(10),
        before_sleep=_log_retry,
    )
    def extract_recipe(self, system_prompt: str, context: str) -> Recipe:
        response = self._client.models.generate_content(
            model=self._model,
            contents=f"{system_prompt}\n\n{context}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Recipe,
            ),
        )
        return Recipe.model_validate_json(response.text)
