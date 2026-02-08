"""Typer CLI application for Uncluttered Recipes."""

from dotenv import load_dotenv

load_dotenv()

from typing import Optional  # noqa: E402

import typer  # noqa: E402

from uncluttered.cli.display import (  # noqa: E402
    console,
    print_recipe_detail,
    print_search_results,
    print_search_terms,
    prompt_selection,
)
from uncluttered.core.database import (  # noqa: E402
    create_tables,
    delete_all_recipes,
    delete_recipe_by_slug,
    delete_recipes_by_search_term,
    get_recipe_by_slug,
    get_recipes_by_search_term,
    get_search_term_counts,
)
from uncluttered.core.engine import process_query  # noqa: E402

app = typer.Typer(
    name="uncluttered",
    help="AI-powered recipe search and extraction. Cooking, clarified.",
    add_completion=False,
)


@app.callback()
def startup():
    """Ensure database tables exist before any command runs."""
    create_tables()


@app.command()
def search(
    query: str = typer.Argument(..., help="Recipe search query"),
    fetch: int = typer.Option(5, "--fetch", "-f", help="Number of recipes to fetch"),
    display: int = typer.Option(3, "--display", "-d", help="Number of recipes to display"),
):
    """Search for recipes and save them to the database."""
    with console.status("[bold green]Hunting for recipes...", spinner="dots"):
        try:
            recipes = process_query(query, fetch_count=fetch, display_count=display)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(1)

    console.print(f'[green]Saved {len(recipes)} recipes for "{query}"[/green]\n')
    print_search_results(recipes, title=f'Top Results for "{query}"')

    choice = prompt_selection(len(recipes))
    if choice is not None:
        print_recipe_detail(recipes[choice - 1])


@app.command("list")
def list_recipes(
    search_term: Optional[str] = typer.Argument(None, help="Search term to filter recipes"),
):
    """List saved recipes. Without arguments, shows all search terms."""
    if search_term is None:
        # Show all search terms
        terms = get_search_term_counts()
        print_search_terms(terms)

        if not terms:
            return

        choice = prompt_selection(len(terms), label="list")
        if choice is None:
            return

        # User picked a search term — show its recipes
        search_term = terms[choice - 1][0]

    recipes = get_recipes_by_search_term(search_term)

    if not recipes:
        console.print(f'[yellow]No recipes found for "{search_term}".[/yellow]')
        console.print(f'Try: [bold]uncluttered search "{search_term}"[/bold]')
        raise typer.Exit(0)

    print_search_results(recipes, title=f'Recipes for "{search_term}"')

    choice = prompt_selection(len(recipes))
    if choice is not None:
        print_recipe_detail(recipes[choice - 1])


@app.command()
def show(slug: str = typer.Argument(..., help="Recipe slug to display")):
    """Show details of a saved recipe by slug."""
    recipe = get_recipe_by_slug(slug)

    if recipe is None:
        console.print(f'[bold red]Error:[/bold red] Recipe with slug "{slug}" not found.')
        raise typer.Exit(1)

    print_recipe_detail(recipe)


@app.command()
def delete(
    slug: Optional[str] = typer.Argument(None, help="Recipe slug to delete"),
    search_term: Optional[str] = typer.Option(
        None, "--search-term", "-s", help="Delete all recipes for a search term"
    ),
    all_recipes: bool = typer.Option(False, "--all", "-a", help="Delete all recipes"),
):
    """Delete recipes by slug, search term, or clear all."""
    # Validate: exactly one option must be specified
    options_set = sum([slug is not None, search_term is not None, all_recipes])
    if options_set == 0:
        console.print("[bold red]Error:[/bold red] Specify a slug, --search-term, or --all")
        raise typer.Exit(1)
    if options_set > 1:
        console.print(
            "[bold red]Error:[/bold red] Specify only one of: slug, --search-term, or --all"
        )
        raise typer.Exit(1)

    # Delete by slug
    if slug:
        if delete_recipe_by_slug(slug):
            console.print(f"[green]Deleted recipe: {slug}[/green]")
        else:
            console.print(f'[bold red]Error:[/bold red] Recipe with slug "{slug}" not found.')
            raise typer.Exit(1)

    # Delete by search term
    elif search_term:
        count = delete_recipes_by_search_term(search_term)
        if count > 0:
            console.print(f'[green]Deleted {count} recipe(s) for "{search_term}"[/green]')
        else:
            console.print(f'[yellow]No recipes found for "{search_term}".[/yellow]')

    # Delete all
    elif all_recipes:
        confirm = typer.confirm("Are you sure you want to delete ALL recipes?")
        if confirm:
            count = delete_all_recipes()
            console.print(f"[green]Deleted {count} recipe(s)[/green]")
        else:
            console.print("[dim]Cancelled.[/dim]")


if __name__ == "__main__":
    app()
