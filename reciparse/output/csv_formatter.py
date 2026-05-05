"""CSV formatter for recipe data."""

import csv
import io
from typing import List, Optional

from reciparse.scrapers.base import RecipeData
from reciparse.output.formatters import FormatterError


CSV_FIELDS = [
    "title",
    "description",
    "ingredients",
    "instructions",
    "prep_time",
    "cook_time",
    "servings",
    "source_url",
]


class CSVFormatter:
    """Formats RecipeData into CSV output."""

    def __init__(self, delimiter: str = ",", list_separator: str = " | ") -> None:
        """
        Args:
            delimiter: CSV column delimiter.
            list_separator: Separator used to join list fields (e.g. ingredients).
        """
        self.delimiter = delimiter
        self.list_separator = list_separator

    def _flatten(self, recipe: RecipeData) -> dict:
        """Convert a RecipeData instance to a flat dict suitable for CSV."""
        data = recipe.to_dict()
        flat = {}
        for field in CSV_FIELDS:
            value = data.get(field, "")
            if isinstance(value, list):
                flat[field] = self.list_separator.join(str(v) for v in value)
            elif value is None:
                flat[field] = ""
            else:
                flat[field] = str(value)
        return flat

    def format_one(self, recipe: RecipeData, include_header: bool = True) -> str:
        """Format a single RecipeData as a CSV string."""
        if not isinstance(recipe, RecipeData):
            raise FormatterError(f"Expected RecipeData, got {type(recipe).__name__}")

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=CSV_FIELDS,
            delimiter=self.delimiter,
            extrasaction="ignore",
            lineterminator="\n",
        )
        if include_header:
            writer.writeheader()
        writer.writerow(self._flatten(recipe))
        return output.getvalue()

    def format_many(self, recipes: List[RecipeData]) -> str:
        """Format multiple RecipeData instances as a CSV string with a single header."""
        if not recipes:
            return ""
        if not all(isinstance(r, RecipeData) for r in recipes):
            raise FormatterError("All items must be RecipeData instances")

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=CSV_FIELDS,
            delimiter=self.delimiter,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for recipe in recipes:
            writer.writerow(self._flatten(recipe))
        return output.getvalue()
