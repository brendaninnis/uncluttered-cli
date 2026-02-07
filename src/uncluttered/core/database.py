"""SQLite database management using SQLAlchemy."""

import json
from pathlib import Path

from sqlalchemy import Column, Integer, String, Text, create_engine, func
from sqlalchemy.orm import declarative_base, sessionmaker

from .models import Ingredient, Recipe, TrustScore

Base = declarative_base()

_engine = None
_SessionLocal = None


def _get_db_path() -> Path:
    """Return the path to the SQLite database file, creating parent dirs if needed."""
    db_path = Path.home() / ".local" / "share" / "uncluttered" / "uncluttered.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def _get_engine():
    """Return a lazily-initialized SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{_get_db_path()}", echo=False)
    return _engine


def _get_session():
    """Return a new session from the lazily-initialized sessionmaker."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=_get_engine())
    return _SessionLocal()


class RecipeTable(Base):
    """SQLAlchemy table for recipes."""

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    ingredients_json = Column(Text, nullable=False)
    instructions_json = Column(Text, nullable=False)
    prep_time = Column(String(50), nullable=True)
    cook_time = Column(String(50), nullable=True)
    serving_yield = Column(String(50), nullable=False)
    source_url = Column(String(500), nullable=True)
    trust_score = Column(Integer, nullable=True)
    trust_reasoning = Column(Text, nullable=True)
    slug = Column(String(255), nullable=True, unique=True, index=True)
    search_term = Column(String(255), nullable=True, index=True)


def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(_get_engine())


def add_recipe(recipe: Recipe) -> Recipe:
    """Save a recipe to the database and return it with its ID."""
    with _get_session() as session:
        db_recipe = RecipeTable(
            title=recipe.title,
            description=recipe.description,
            ingredients_json=json.dumps([ing.model_dump() for ing in recipe.ingredients]),
            instructions_json=json.dumps(recipe.instructions),
            prep_time=recipe.prep_time,
            cook_time=recipe.cook_time,
            serving_yield=recipe.serving_yield,
            source_url=recipe.source_url,
            trust_score=recipe.trust_score.score if recipe.trust_score else None,
            trust_reasoning=recipe.trust_score.reasoning if recipe.trust_score else None,
            slug=recipe.slug,
            search_term=recipe.search_term,
        )
        session.add(db_recipe)
        session.commit()
        session.refresh(db_recipe)

        # Return the recipe with its new ID
        return _row_to_recipe(db_recipe)


def get_recipe(recipe_id: int) -> Recipe | None:
    """Retrieve a recipe by ID."""
    with _get_session() as session:
        db_recipe = session.query(RecipeTable).filter(RecipeTable.id == recipe_id).first()
        if db_recipe is None:
            return None
        return _row_to_recipe(db_recipe)


def get_all_recipes() -> list[Recipe]:
    """Retrieve all recipes from the database."""
    with _get_session() as session:
        rows = session.query(RecipeTable).order_by(RecipeTable.id.desc()).all()
        return [_row_to_recipe(row) for row in rows]


def _row_to_recipe(row: RecipeTable) -> Recipe:
    """Convert a database row to a Recipe model."""
    ingredients = [Ingredient(**ing) for ing in json.loads(row.ingredients_json)]
    trust_score = None
    if row.trust_score is not None:
        trust_score = TrustScore(score=row.trust_score, reasoning=row.trust_reasoning or "")

    return Recipe(
        id=row.id,
        title=row.title,
        description=row.description,
        ingredients=ingredients,
        instructions=json.loads(row.instructions_json),
        prep_time=row.prep_time,
        cook_time=row.cook_time,
        serving_yield=row.serving_yield,
        source_url=row.source_url,
        trust_score=trust_score,
        slug=row.slug,
        search_term=row.search_term,
    )


def get_recipe_by_slug(slug: str) -> Recipe | None:
    """Retrieve a recipe by its slug."""
    with _get_session() as session:
        db_recipe = session.query(RecipeTable).filter(RecipeTable.slug == slug).first()
        if db_recipe is None:
            return None
        return _row_to_recipe(db_recipe)


def get_recipes_by_search_term(search_term: str) -> list[Recipe]:
    """Retrieve all recipes for a given search term (case-insensitive)."""
    with _get_session() as session:
        rows = (
            session.query(RecipeTable)
            .filter(func.lower(RecipeTable.search_term) == search_term.lower())
            .order_by(RecipeTable.trust_score.desc())
            .all()
        )
        return [_row_to_recipe(row) for row in rows]


def get_saved_urls_by_search_term(search_term: str) -> list[str]:
    """Get all source URLs for a given search term (case-insensitive)."""
    with _get_session() as session:
        rows = (
            session.query(RecipeTable.source_url)
            .filter(func.lower(RecipeTable.search_term) == search_term.lower())
            .filter(RecipeTable.source_url.isnot(None))
            .all()
        )
        return [row[0] for row in rows]


def get_all_search_terms() -> list[str]:
    """Get all unique search terms from the database."""
    with _get_session() as session:
        rows = session.query(RecipeTable.search_term).distinct().all()
        return [row[0] for row in rows if row[0] is not None]


def get_search_term_counts() -> list[tuple[str, int]]:
    """Get all search terms with recipe counts."""
    with _get_session() as session:
        rows = (
            session.query(
                RecipeTable.search_term,
                func.count(RecipeTable.id),
            )
            .filter(RecipeTable.search_term.isnot(None))
            .group_by(RecipeTable.search_term)
            .all()
        )
        return [(row[0], row[1]) for row in rows]


def get_all_slugs() -> set[str]:
    """Get all existing slugs from the database."""
    with _get_session() as session:
        rows = session.query(RecipeTable.slug).all()
        return {row[0] for row in rows if row[0] is not None}


def delete_recipe_by_slug(slug: str) -> bool:
    """Delete a recipe by its slug. Returns True if deleted, False if not found."""
    with _get_session() as session:
        result = session.query(RecipeTable).filter(RecipeTable.slug == slug).delete()
        session.commit()
        return result > 0


def delete_recipes_by_search_term(search_term: str) -> int:
    """Delete all recipes for a search term (case-insensitive). Returns count of deleted recipes."""
    with _get_session() as session:
        result = (
            session.query(RecipeTable)
            .filter(func.lower(RecipeTable.search_term) == search_term.lower())
            .delete()
        )
        session.commit()
        return result


def delete_all_recipes() -> int:
    """Delete all recipes from the database. Returns count of deleted recipes."""
    with _get_session() as session:
        result = session.query(RecipeTable).delete()
        session.commit()
        return result
