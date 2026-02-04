"""Pydantic models for recipe data."""

from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    """A single ingredient with quantity and unit."""
    name: str
    quantity: str
    unit: str | None = None


class TrustScore(BaseModel):
    """Trust score for a recipe with reasoning."""
    score: int = Field(..., ge=0, le=100, description="Trust score from 0-100")
    reasoning: str = Field(..., description="Explanation for the score")


class Recipe(BaseModel):
    """A complete recipe extracted from search results."""
    id: int | None = None
    title: str
    description: str
    ingredients: list[Ingredient]
    instructions: list[str]
    prep_time: str | None = None
    cook_time: str | None = None
    serving_yield: str = Field(..., alias="yield", description="Number of servings")
    source_url: str | None = None
    trust_score: TrustScore | None = None
    slug: str | None = None
    search_term: str | None = None

    model_config = {
        "populate_by_name": True,
    }
