"""OpenAI recipe provider."""

import os

from openai import OpenAI, RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..models import Recipe
from .base import RecipeProvider


def _log_retry(retry_state):
    """Log retry attempts to the console."""
    sleep_time = retry_state.next_action.sleep
    print(
        f"  OpenAI is busy. Retrying in {sleep_time:.1f}s... "
        f"(attempt {retry_state.attempt_number}/10)"
    )


class OpenAIProvider(RecipeProvider):
    """Recipe extraction using OpenAI."""

    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, model: str | None = None):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Get your key at: https://platform.openai.com/api-keys"
            )
        self._client = OpenAI(api_key=api_key)
        self._model = model or self.DEFAULT_MODEL

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        wait=wait_exponential(multiplier=2, min=2, max=60),
        stop=stop_after_attempt(10),
        before_sleep=_log_retry,
    )
    def extract_recipe(self, system_prompt: str, context: str) -> Recipe:
        schema = Recipe.model_json_schema()
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "recipe",
                    "strict": True,
                    "schema": schema,
                },
            },
        )
        return Recipe.model_validate_json(response.choices[0].message.content)
