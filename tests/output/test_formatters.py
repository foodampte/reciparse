"""Tests for reciparse.output.formatters."""

import csv
import io
import json

import pytest

from reciparse.scrapers.base import RecipeData
from reciparse.output.formatters import (
    CSVFormatter,
    FormatterError,
    JSONFormatter,
    get_formatter,
)


@pytest.fixture()
def sample_recipe() -> RecipeData:
    return RecipeData(
        title="Spaghetti Carbonara",
        description="A classic Roman pasta dish.",
        ingredients=["200g spaghetti", "100g pancetta", "2 eggs", "50g pecorino"],
        instructions=["Boil pasta.", "Fry pancetta.", "Mix eggs and cheese.", "Combine."],
        prep_time="10 mins",
        cook_time="20 mins",
        servings="2",
        source_url="https://example.com/carbonara",
    )


@pytest.fixture()
def minimal_recipe() -> RecipeData:
    return RecipeData(title="Plain Toast")


# ---------------------------------------------------------------------------
# JSONFormatter
# ---------------------------------------------------------------------------

class TestJSONFormatter:
    def test_format_one_returns_valid_json(self, sample_recipe):
        formatter = JSONFormatter()
        result = formatter.format_one(sample_recipe)
        data = json.loads(result)
        assert data["title"] == "Spaghetti Carbonara"
        assert isinstance(data["ingredients"], list)
        assert len(data["ingredients"]) == 4

    def test_format_one_includes_all_keys(self, sample_recipe):
        formatter = JSONFormatter()
        data = json.loads(formatter.format_one(sample_recipe))
        expected_keys = {
            "title", "description", "ingredients", "instructions",
            "prep_time", "cook_time", "servings", "source_url",
        }
        assert expected_keys.issubset(data.keys())

    def test_format_many_returns_json_array(self, sample_recipe, minimal_recipe):
        formatter = JSONFormatter()
        result = formatter.format_many([sample_recipe, minimal_recipe])
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["title"] == "Spaghetti Carbonara"
        assert data[1]["title"] == "Plain Toast"

    def test_format_many_empty_list(self):
        formatter = JSONFormatter()
        result = formatter.format_many([])
        assert json.loads(result) == []

    def test_custom_indent(self, sample_recipe):
        formatter = JSONFormatter(indent=4)
        result = formatter.format_one(sample_recipe)
        # 4-space indent means lines start with 4 spaces
        assert "    " in result


# ---------------------------------------------------------------------------
# CSVFormatter
# ---------------------------------------------------------------------------

class TestCSVFormatter:
    def test_format_one_has_header_and_data_row(self, sample_recipe):
        formatter = CSVFormatter()
        result = formatter.format_one(sample_recipe)
        lines = result.strip().splitlines()
        assert len(lines) == 2  # header + 1 data row
        assert "title" in lines[0]

    def test_format_one_title_in_output(self, sample_recipe):
        formatter = CSVFormatter()
        result = formatter.format_one(sample_recipe)
        assert "Spaghetti Carbonara" in result

    def test_ingredients_pipe_separated(self, sample_recipe):
        formatter = CSVFormatter()
        result = formatter.format_one(sample_recipe)
        reader = csv.DictReader(io.StringIO(result))
        row = next(reader)
        assert " | " in row["ingredients"]
        assert "200g spaghetti" in row["ingredients"]

    def test_format_many_row_count(self, sample_recipe, minimal_recipe):
        formatter = CSVFormatter()
        result = formatter.format_many([sample_recipe, minimal_recipe])
        lines = result.strip().splitlines()
        assert len(lines) == 3  # header + 2 rows

    def test_minimal_recipe_empty_fields(self, minimal_recipe):
        formatter = CSVFormatter()
        result = formatter.format_one(minimal_recipe)
        reader = csv.DictReader(io.StringIO(result))
        row = next(reader)
        assert row["title"] == "Plain Toast"
        assert row["description"] == ""


# ---------------------------------------------------------------------------
# get_formatter factory
# ---------------------------------------------------------------------------

class TestGetFormatter:
    def test_returns_json_formatter(self):
        assert isinstance(get_formatter("json"), JSONFormatter)

    def test_returns_csv_formatter(self):
        assert isinstance(get_formatter("csv"), CSVFormatter)

    def test_case_insensitive(self):
        assert isinstance(get_formatter("JSON"), JSONFormatter)
        assert isinstance(get_formatter("CSV"), CSVFormatter)

    def test_unsupported_format_raises(self):
        with pytest.raises(FormatterError, match="Unsupported output format"):
            get_formatter("xml")
