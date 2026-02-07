"""Rich display utilities for the CLI."""

import sys

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from uncluttered.core.models import Recipe

console = Console()


def _score_color(score: int) -> str:
    """Return color based on trust score."""
    if score >= 80:
        return "green"
    elif score >= 50:
        return "yellow"
    else:
        return "red"


def print_search_results(recipes: list[Recipe], title: str | None = None) -> None:
    """Render a Rich Table of recipes."""
    if not recipes:
        console.print("[dim]No recipes found.[/dim]")
        return

    table_title = title or "Saved Recipes"
    table = Table(
        title=table_title,
        show_header=True,
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("#", justify="right", width=3)
    table.add_column("Recipe", style="bold")
    table.add_column("Trust Score", justify="center", width=12)

    for i, recipe in enumerate(recipes, 1):
        score = recipe.trust_score.score if recipe.trust_score else 0
        color = _score_color(score)
        score_display = f"[{color}]{score}/100[/{color}]"

        slug = recipe.slug or "N/A"
        # Title on first line, slug below in dim
        recipe_cell = f"{recipe.title}\n[dim]{slug}[/dim]"

        table.add_row(str(i), recipe_cell, score_display)

    console.print(table)


def print_recipe_detail(recipe: Recipe) -> None:
    """Render a detailed recipe view."""
    # Build ingredients list
    ingredients_md = "\n".join(
        f"- {ing.quantity} {ing.unit or ''} {ing.name}".strip()
        for ing in recipe.ingredients
    )

    # Build instructions list
    instructions_md = "\n".join(
        f"{i}. {step}"
        for i, step in enumerate(recipe.instructions, 1)
    )

    # Build metadata line
    meta_parts = []
    if recipe.prep_time:
        meta_parts.append(f"Prep: {recipe.prep_time}")
    if recipe.cook_time:
        meta_parts.append(f"Cook: {recipe.cook_time}")
    if recipe.serving_yield:
        meta_parts.append(f"Yield: {recipe.serving_yield}")
    meta_line = "  |  ".join(meta_parts) if meta_parts else ""

    # Trust score display (plain text for markdown compatibility)
    score_section = ""
    if recipe.trust_score:
        score = recipe.trust_score.score
        score_section = f"\n\n---\n\n**Trust Score:** {score}/100\n\n_{recipe.trust_score.reasoning}_"

    # Source
    source_section = ""
    if recipe.source_url:
        source_section = f"\n\n**Source:** {recipe.source_url}"

    # Compose full markdown
    md_content = f"""## {recipe.title}

_{recipe.description}_

{meta_line}

---

### Ingredients

{ingredients_md}

---

### Instructions

{instructions_md}{score_section}{source_section}
"""

    # Use slug if available, otherwise fall back to ID
    panel_title = recipe.slug or f"Recipe #{recipe.id}"
    panel = Panel(
        Markdown(md_content),
        title=f"[bold cyan]{panel_title}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)


def print_search_terms(terms: list[tuple[str, int]]) -> None:
    """Render a numbered table of search terms with recipe counts."""
    if not terms:
        console.print("[dim]No saved recipes yet.[/dim]")
        return

    table = Table(
        title="Search Terms",
        show_header=True,
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("#", justify="right", width=3)
    table.add_column("Search Term", style="bold")
    table.add_column("Recipes", justify="center", width=8)

    for i, (term, count) in enumerate(terms, 1):
        table.add_row(str(i), term, str(count))

    console.print(table)


def prompt_selection(count: int, label: str = "show") -> int | None:
    """Prompt the user to select a numbered item. Returns 1-indexed int or None."""
    if not sys.stdin.isatty():
        return None

    try:
        raw = console.input(f"Enter # to {label} (or Enter to skip): ")
    except EOFError:
        return None

    raw = raw.strip()
    if not raw:
        return None

    try:
        choice = int(raw)
    except ValueError:
        console.print("[yellow]Invalid input, skipping.[/yellow]")
        return None

    if choice < 1 or choice > count:
        console.print(f"[yellow]Please enter a number between 1 and {count}.[/yellow]")
        return None

    return choice
