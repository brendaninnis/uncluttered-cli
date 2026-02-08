"""Tests for Pydantic data models."""

import pytest
from pydantic import ValidationError

from uncluttered.core.models import Ingredient, Recipe, TrustScore


class TestIngredient:
    def test_with_unit(self):
        ing = Ingredient(name="flour", quantity="2", unit="cups")
        assert ing.name == "flour"
        assert ing.quantity == "2"
        assert ing.unit == "cups"

    def test_without_unit(self):
        ing = Ingredient(name="salt", quantity="1 pinch")
        assert ing.unit is None


class TestTrustScore:
    def test_valid_score(self):
        ts = TrustScore(score=85, reasoning="Well-structured recipe")
        assert ts.score == 85

    def test_score_at_bounds(self):
        TrustScore(score=0, reasoning="Poor")
        TrustScore(score=100, reasoning="Perfect")

    def test_score_below_zero_rejected(self):
        with pytest.raises(ValidationError):
            TrustScore(score=-1, reasoning="Invalid")

    def test_score_above_100_rejected(self):
        with pytest.raises(ValidationError):
            TrustScore(score=101, reasoning="Invalid")


class TestRecipe:
    @pytest.fixture
    def minimal_recipe_data(self):
        return {
            "title": "Test Recipe",
            "description": "A test",
            "ingredients": [{"name": "flour", "quantity": "1", "unit": "cup"}],
            "instructions": ["Mix", "Bake"],
            "yield": "4 servings",
        }

    def test_minimal_recipe(self, minimal_recipe_data):
        recipe = Recipe(**minimal_recipe_data)
        assert recipe.title == "Test Recipe"
        assert recipe.serving_yield == "4 servings"
        assert recipe.id is None
        assert recipe.source_url is None
        assert recipe.trust_score is None

    def test_recipe_with_all_fields(self, minimal_recipe_data):
        data = {
            **minimal_recipe_data,
            "prep_time": "10 min",
            "cook_time": "30 min",
            "source_url": "https://example.com/recipe",
            "trust_score": {"score": 75, "reasoning": "Good recipe"},
            "slug": "test-recipe",
            "search_term": "test",
        }
        recipe = Recipe(**data)
        assert recipe.prep_time == "10 min"
        assert recipe.trust_score.score == 75
        assert recipe.slug == "test-recipe"

    def test_missing_required_field_rejected(self):
        with pytest.raises(ValidationError):
            Recipe(title="No yield", description="Oops", ingredients=[], instructions=[])
