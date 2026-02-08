"""Ollama recipe provider (local LLM via OpenAI-compatible API)."""

import json
import logging
import os

from openai import APIConnectionError, OpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..models import Recipe
from .base import RecipeProvider

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:11434/v1"


def _log_retry(retry_state):
    """Log retry attempts."""
    sleep_time = retry_state.next_action.sleep
    logger.info(
        "Ollama connection failed. Retrying in %.1fs (attempt %d/10)",
        sleep_time,
        retry_state.attempt_number,
    )


class OllamaProvider(RecipeProvider):
    """Recipe extraction using a local Ollama model.

    Uses Ollama's OpenAI-compatible API with JSON object mode.
    The recipe JSON schema is included in the system prompt for guidance.
    """

    def __init__(self, model: str | None = None):
        if not model:
            raise ValueError(
                "LLM_MODEL environment variable is required for Ollama. "
                "Set it to a model you have pulled (e.g. llama3.1, mistral)."
            )
        base_url = os.getenv("OLLAMA_BASE_URL", DEFAULT_BASE_URL)
        self._client = OpenAI(base_url=base_url, api_key="ollama")
        self._model = model

    @retry(
        retry=retry_if_exception_type(APIConnectionError),
        wait=wait_exponential(multiplier=2, min=2, max=60),
        stop=stop_after_attempt(10),
        before_sleep=_log_retry,
    )
    def extract_recipe(self, system_prompt: str, context: str) -> Recipe:
        schema = Recipe.model_json_schema()
        schema_instruction = (
            "You MUST respond with valid JSON matching this schema:\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```"
        )
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": f"{system_prompt}\n\n{schema_instruction}"},
                {"role": "user", "content": context},
            ],
            response_format={"type": "json_object"},
        )
        return Recipe.model_validate_json(response.choices[0].message.content)
