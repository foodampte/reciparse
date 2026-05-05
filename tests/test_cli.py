"""Tests for the reciparse CLI entry point."""

from unittest.mock import MagicMock, patch

import pytest

from reciparse.cli import build_parser, run
from reciparse.scrapers.base import RecipeData
from reciparse.scrapers.registry import UnsupportedSiteError


ALLRECIPES_URL = "https://www.allrecipes.com/recipe/12345/test-recipe/"


@pytest.fixture()
def mock_recipe():
    return RecipeData(
        title="Chocolate Cake",
        description="Rich and moist.",
        ingredients=["2 cups flour", "1 cup sugar"],
        instructions=["Mix dry ingredients.", "Bake at 350F."],
        prep_time="15 min",
        cook_time="30 min",
        servings="8",
        image_url="https://example.com/cake.jpg",
    )


def test_build_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([ALLRECIPES_URL])
    assert args.url == ALLRECIPES_URL
    assert args.format == "json"
    assert args.output is None
    assert args.indent == 2


def test_build_parser_csv_format():
    parser = build_parser()
    args = parser.parse_args([ALLRECIPES_URL, "--format", "csv"])
    assert args.format == "csv"


def test_run_returns_zero_on_success(mock_recipe, capsys):
    with patch("reciparse.cli.ScraperRegistry") as MockRegistry:
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = mock_recipe
        MockRegistry.return_value.get_scraper.return_value = mock_scraper

        result = run([ALLRECIPES_URL])

    assert result == 0
    captured = capsys.readouterr()
    assert "Chocolate Cake" in captured.out


def test_run_unsupported_site_returns_one(capsys):
    with patch("reciparse.cli.ScraperRegistry") as MockRegistry:
        MockRegistry.return_value.get_scraper.side_effect = UnsupportedSiteError(
            "https://unknown.com"
        )
        result = run(["https://unknown.com/recipe/"])

    assert result == 1
    captured = capsys.readouterr()
    assert "error" in captured.err


def test_run_scrape_exception_returns_one(capsys):
    with patch("reciparse.cli.ScraperRegistry") as MockRegistry:
        mock_scraper = MagicMock()
        mock_scraper.scrape.side_effect = RuntimeError("network timeout")
        MockRegistry.return_value.get_scraper.return_value = mock_scraper

        result = run([ALLRECIPES_URL])

    assert result == 1
    assert "network timeout" in capsys.readouterr().err


def test_run_csv_format(mock_recipe, capsys):
    with patch("reciparse.cli.ScraperRegistry") as MockRegistry:
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = mock_recipe
        MockRegistry.return_value.get_scraper.return_value = mock_scraper

        result = run([ALLRECIPES_URL, "--format", "csv"])

    assert result == 0
    captured = capsys.readouterr()
    assert "title" in captured.out
    assert "Chocolate Cake" in captured.out


def test_run_output_to_file(mock_recipe, tmp_path):
    out_file = tmp_path / "recipe.json"
    with patch("reciparse.cli.ScraperRegistry") as MockRegistry:
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = mock_recipe
        MockRegistry.return_value.get_scraper.return_value = mock_scraper

        result = run([ALLRECIPES_URL, "--output", str(out_file)])

    assert result == 0
    content = out_file.read_text(encoding="utf-8")
    assert "Chocolate Cake" in content
