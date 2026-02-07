"""Anthropic recipe provider."""

import os

import anthropic
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..models import Recipe
from .base import RecipeProvider


def _log_retry(retry_state):
    """Log retry attempts to the console."""
    sleep_time = retry_state.next_action.sleep
    print(
        f"  Anthropic is busy. Retrying in {sleep_time:.1f}s... "
        f"(attempt {retry_state.attempt_number}/10)"
    )


class AnthropicProvider(RecipeProvider):
    """Recipe extraction using Anthropic Claude."""

    DEFAULT_MODEL = "claude-sonnet-4-5-20250929"

    def __init__(self, model: str | None = None):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required. "
                "Get your key at: https://console.anthropic.com/settings/keys"
            )
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model or self.DEFAULT_MODEL

    @retry(
        retry=retry_if_exception_type(anthropic.RateLimitError),
        wait=wait_exponential(multiplier=2, min=2, max=60),
        stop=stop_after_attempt(10),
        before_sleep=_log_retry,
    )
    def extract_recipe(self, system_prompt: str, context: str) -> Recipe:
        schema = Recipe.model_json_schema()
        response = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": context}],
            tools=[
                {
                    "name": "save_recipe",
                    "description": "Save the extracted recipe data.",
                    "input_schema": schema,
                }
            ],
            tool_choice={"type": "tool", "name": "save_recipe"},
        )
        for block in response.content:
            if block.type == "tool_use":
                return Recipe.model_validate(block.input)
        raise ValueError("No tool_use block found in Anthropic response")
