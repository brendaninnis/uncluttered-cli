"""Utility functions for recipe processing."""

import re
import unicodedata


def generate_slug(title: str) -> str:
    """
    Convert a recipe title to a URL-friendly slug.

    Args:
        title: The recipe title (e.g., "Grandma's Chocolate Chip Cookies!")

    Returns:
        A lowercase, hyphenated slug (e.g., "grandmas-chocolate-chip-cookies")
    """
    # Normalize unicode characters
    slug = unicodedata.normalize("NFKD", title)
    # Remove non-ASCII characters
    slug = slug.encode("ascii", "ignore").decode("ascii")
    # Convert to lowercase
    slug = slug.lower()
    # Replace apostrophes and special chars with nothing
    slug = re.sub(r"[''`]", "", slug)
    # Replace any non-alphanumeric characters with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)

    return slug


def make_unique_slug(base_slug: str, existing_slugs: set[str]) -> str:
    """
    Ensure a slug is unique by appending a number if necessary.

    Args:
        base_slug: The base slug to make unique
        existing_slugs: Set of slugs that already exist

    Returns:
        A unique slug (e.g., "chocolate-chip-cookies-2" if original exists)
    """
    if base_slug not in existing_slugs:
        return base_slug

    counter = 2
    while f"{base_slug}-{counter}" in existing_slugs:
        counter += 1

    return f"{base_slug}-{counter}"
