"""Output formatters for converting RecipeData to JSON or CSV."""

import csv
import json
import io
from typing import List, Union

from reciparse.scrapers.base import RecipeData


class FormatterError(Exception):
    """Raised when formatting fails."""
    pass


class JSONFormatter:
    """Formats RecipeData as JSON."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def format_one(self, recipe: RecipeData) -> str:
        """Serialize a single RecipeData to a JSON string."""
        try:
            return json.dumps(recipe.to_dict(), indent=self.indent, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise FormatterError(f"Failed to serialize recipe to JSON: {exc}") from exc

    def format_many(self, recipes: List[RecipeData]) -> str:
        """Serialize a list of RecipeData objects to a JSON array string."""
        try:
            return json.dumps(
                [r.to_dict() for r in recipes],
                indent=self.indent,
                ensure_ascii=False,
            )
        except (TypeError, ValueError) as exc:
            raise FormatterError(f"Failed to serialize recipes to JSON: {exc}") from exc


class CSVFormatter:
    """Formats RecipeData as CSV."""

    FIELDS = [
        "title",
        "description",
        "ingredients",
        "instructions",
        "prep_time",
        "cook_time",
        "servings",
        "source_url",
    ]

    def _flatten(self, recipe: RecipeData) -> dict:
        """Flatten list fields to pipe-separated strings for CSV output."""
        data = recipe.to_dict()
        for key in ("ingredients", "instructions"):
            value = data.get(key)
            if isinstance(value, list):
                data[key] = " | ".join(str(v) for v in value)
        return data

    def format_one(self, recipe: RecipeData) -> str:
        """Serialize a single RecipeData to a CSV string (with header)."""
        return self.format_many([recipe])

    def format_many(self, recipes: List[RecipeData]) -> str:
        """Serialize a list of RecipeData objects to a CSV string."""
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=self.FIELDS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for recipe in recipes:
            writer.writerow(self._flatten(recipe))
        return output.getvalue()


def get_formatter(fmt: str) -> Union[JSONFormatter, CSVFormatter]:
    """Return the appropriate formatter instance for the given format string."""
    fmt = fmt.lower().strip()
    if fmt == "json":
        return JSONFormatter()
    if fmt == "csv":
        return CSVFormatter()
    raise FormatterError(f"Unsupported output format: '{fmt}'. Choose 'json' or 'csv'.")
