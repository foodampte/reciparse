"""Tests for CSVFormatter."""

import csv
import io
import pytest

from reciparse.scrapers.base import RecipeData
from reciparse.output.csv_formatter import CSVFormatter, CSV_FIELDS
from reciparse.output.formatters import FormatterError


@pytest.fixture
def sample_recipe():
    return RecipeData(
        title="Spaghetti Bolognese",
        description="A classic Italian meat sauce.",
        ingredients=["200g spaghetti", "100g beef mince", "1 onion"],
        instructions=["Boil pasta.", "Brown mince.", "Combine and serve."],
        prep_time="10 mins",
        cook_time="30 mins",
        servings="2",
        source_url="https://example.com/bolognese",
    )


@pytest.fixture
def minimal_recipe():
    return RecipeData(title="Plain Toast")


@pytest.fixture
def formatter():
    return CSVFormatter()


def test_format_one_returns_string(formatter, sample_recipe):
    result = formatter.format_one(sample_recipe)
    assert isinstance(result, str)


def test_format_one_includes_header(formatter, sample_recipe):
    result = formatter.format_one(sample_recipe, include_header=True)
    first_line = result.splitlines()[0]
    for field in CSV_FIELDS:
        assert field in first_line


def test_format_one_without_header(formatter, sample_recipe):
    result = formatter.format_one(sample_recipe, include_header=False)
    first_line = result.splitlines()[0]
    assert "title" not in first_line
    assert "Spaghetti Bolognese" in first_line


def test_format_one_joins_list_fields(formatter, sample_recipe):
    result = formatter.format_one(sample_recipe)
    assert "200g spaghetti | 100g beef mince | 1 onion" in result


def test_format_one_custom_list_separator():
    fmt = CSVFormatter(list_separator=";")
    recipe = RecipeData(title="Test", ingredients=["a", "b", "c"])
    result = fmt.format_one(recipe)
    assert "a;b;c" in result


def test_format_one_handles_missing_fields(formatter, minimal_recipe):
    result = formatter.format_one(minimal_recipe)
    reader = csv.DictReader(io.StringIO(result))
    row = next(reader)
    assert row["title"] == "Plain Toast"
    assert row["description"] == ""
    assert row["ingredients"] == ""


def test_format_one_raises_for_invalid_input(formatter):
    with pytest.raises(FormatterError):
        formatter.format_one({"title": "Not a RecipeData"})


def test_format_many_single_header(formatter, sample_recipe, minimal_recipe):
    result = formatter.format_many([sample_recipe, minimal_recipe])
    lines = result.strip().splitlines()
    # Header + 2 data rows
    assert len(lines) == 3
    assert "title" in lines[0]


def test_format_many_empty_returns_empty_string(formatter):
    assert formatter.format_many([]) == ""


def test_format_many_raises_for_invalid_items(formatter, sample_recipe):
    with pytest.raises(FormatterError):
        formatter.format_many([sample_recipe, "not a recipe"])


def test_format_many_correct_row_count(formatter, sample_recipe):
    recipes = [sample_recipe] * 5
    result = formatter.format_many(recipes)
    lines = result.strip().splitlines()
    assert len(lines) == 6  # 1 header + 5 rows
