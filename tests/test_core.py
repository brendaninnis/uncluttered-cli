"""Test script to verify core database functionality."""

from uncluttered.core.models import Recipe, Ingredient, TrustScore
from uncluttered.core.database import create_tables, add_recipe, get_recipe


def main():
    # Create tables
    print("Creating database tables...")
    create_tables()
    print("Tables created\n")

    # Create a dummy recipe
    dummy_recipe = Recipe(
        title="Classic Spaghetti Carbonara",
        description="A creamy Italian pasta dish made with eggs, cheese, and pancetta.",
        ingredients=[
            Ingredient(name="spaghetti", quantity="400", unit="g"),
            Ingredient(name="pancetta", quantity="200", unit="g"),
            Ingredient(name="eggs", quantity="4", unit=None),
            Ingredient(name="parmesan cheese", quantity="100", unit="g"),
            Ingredient(name="black pepper", quantity="to taste", unit=None),
        ],
        instructions=[
            "Bring a large pot of salted water to boil and cook spaghetti according to package directions.",
            "While pasta cooks, fry pancetta in a large pan until crispy.",
            "In a bowl, whisk together eggs and grated parmesan.",
            "Drain pasta, reserving 1 cup of pasta water.",
            "Toss hot pasta with pancetta, then remove from heat.",
            "Quickly stir in egg mixture, adding pasta water as needed for creaminess.",
            "Season generously with black pepper and serve immediately.",
        ],
        prep_time="10 minutes",
        cook_time="20 minutes",
        serving_yield="4 servings",
        source_url="https://example.com/carbonara",
        trust_score=TrustScore(
            score=85,
            reasoning="Classic recipe with authentic ingredients. Clear instructions."
        ),
    )

    print("Saving recipe to database...")
    saved_recipe = add_recipe(dummy_recipe)
    print(f"Recipe saved with ID: {saved_recipe.id}\n")

    # Retrieve the recipe
    print(f"Retrieving recipe with ID {saved_recipe.id}...")
    retrieved = get_recipe(saved_recipe.id)

    if retrieved:
        print("Recipe retrieved successfully!\n")
        print("=" * 50)
        print(f"Title: {retrieved.title}")
        print(f"Description: {retrieved.description}")
        print(f"Prep Time: {retrieved.prep_time}")
        print(f"Cook Time: {retrieved.cook_time}")
        print(f"Yield: {retrieved.serving_yield}")
        print(f"Source: {retrieved.source_url}")
        print(f"\nIngredients ({len(retrieved.ingredients)}):")
        for ing in retrieved.ingredients:
            unit = f" {ing.unit}" if ing.unit else ""
            print(f"  - {ing.quantity}{unit} {ing.name}")
        print(f"\nInstructions ({len(retrieved.instructions)} steps):")
        for i, step in enumerate(retrieved.instructions, 1):
            print(f"  {i}. {step}")
        if retrieved.trust_score:
            print(f"\nTrust Score: {retrieved.trust_score.score}/100")
            print(f"Reasoning: {retrieved.trust_score.reasoning}")
        print("=" * 50)
    else:
        print("Failed to retrieve recipe!")


if __name__ == "__main__":
    main()
