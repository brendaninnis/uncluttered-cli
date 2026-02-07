"""Abstract base class for LLM recipe providers."""

from abc import ABC, abstractmethod

from ..models import Recipe


class RecipeProvider(ABC):
    """Base class for LLM providers that extract recipes."""

    @abstractmethod
    def extract_recipe(self, system_prompt: str, context: str) -> Recipe:
        """Extract a structured Recipe from context using an LLM.

        Args:
            system_prompt: The system instructions for the LLM.
            context: The user message with recipe content to extract.

        Returns:
            A validated Recipe object.
        """
        ...
