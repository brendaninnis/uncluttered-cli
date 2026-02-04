"""Test script for Phase 2: The Agentic Pipeline."""

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from uncluttered.core.engine import process_query


def main():
    print("=" * 60)
    print("Phase 2 Test: Agentic Pipeline")
    print("=" * 60)
    print()

    query = "Best Carbonara"
    print(f"Searching for: {query}")
    print("-" * 40)
    print()

    try:
        recipes = process_query(query)

        for recipe in recipes:
            print(f"Recipe saved with ID: {recipe.id}")
            print()
            print("=" * 60)
            print(f"TITLE: {recipe.title}")
            print("=" * 60)
            print()
            print(f"Description: {recipe.description}")
            print()
            print(f"Prep Time: {recipe.prep_time or 'Not specified'}")
            print(f"Cook Time: {recipe.cook_time or 'Not specified'}")
            print(f"Yield: {recipe.serving_yield}")
            print(f"Source: {recipe.source_url or 'Not specified'}")
            print()

            print("INGREDIENTS:")
            print("-" * 40)
            for ing in recipe.ingredients:
                unit = f" {ing.unit}" if ing.unit else ""
                print(f"  - {ing.quantity}{unit} {ing.name}")
            print()

            print("INSTRUCTIONS:")
            print("-" * 40)
            for i, step in enumerate(recipe.instructions, 1):
                print(f"  {i}. {step}")
            print()

            if recipe.trust_score:
                print("=" * 60)
                print(f"TRUST SCORE: {recipe.trust_score.score}/100")
                print("=" * 60)
                print(f"Reasoning: {recipe.trust_score.reasoning}")
            print()
            print()

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
