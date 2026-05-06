"""Tests for the Delish.com scraper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from reciparse.scrapers.delish import DelishScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture()
def scraper() -> DelishScraper:
    return DelishScraper()


# ---------------------------------------------------------------------------
# supports()
# ---------------------------------------------------------------------------

def test_supports_delish_url(scraper: DelishScraper) -> None:
    assert scraper.supports("https://www.delish.com/cooking/recipe-ideas/a123/chocolate-cake/")


def test_supports_delish_no_www(scraper: DelishScraper) -> None:
    assert scraper.supports("https://delish.com/cooking/recipe-ideas/a99/pasta/")


def test_does_not_support_other_url(scraper: DelishScraper) -> None:
    assert not scraper.supports("https://www.allrecipes.com/recipe/12345/")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_response(html: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


_FULL_HTML = """
<html><body>
  <h1 class="recipe-title">Chocolate Lava Cake</h1>
  <div class="recipe-intro">A rich, gooey dessert.</div>
  <ul class="ingredient-list">
    <li>1 cup flour</li>
    <li>2 eggs</li>
    <li>100g chocolate</li>
  </ul>
  <ol class="direction-list">
    <li>Preheat oven to 200C.</li>
    <li>Mix ingredients.</li>
    <li>Bake for 12 minutes.</li>
  </ol>
  <span data-time-type="prep">15 mins</span>
  <span data-time-type="cook">12 mins</span>
  <span class="servings">4 servings</span>
</body></html>
"""


@patch("reciparse.scrapers.delish.requests.get")
def test_scrape_returns_recipe_data(mock_get: MagicMock, scraper: DelishScraper) -> None:
    mock_get.return_value = _make_mock_response(_FULL_HTML)
    url = "https://www.delish.com/cooking/recipe-ideas/a1/chocolate-lava-cake/"
    result = scraper.scrape(url)

    assert isinstance(result, RecipeData)
    assert result.title == "Chocolate Lava Cake"
    assert result.description == "A rich, gooey dessert."
    assert len(result.ingredients) == 3
    assert result.ingredients[0] == "1 cup flour"
    assert len(result.instructions) == 3
    assert result.prep_time == "15 mins"
    assert result.cook_time == "12 mins"
    assert result.servings == "4 servings"
    assert result.source_url == url


@patch("reciparse.scrapers.delish.requests.get")
def test_scrape_handles_missing_fields(mock_get: MagicMock, scraper: DelishScraper) -> None:
    """Scraper should return empty strings / lists for absent elements."""
    mock_get.return_value = _make_mock_response("<html><body><h1>Minimal</h1></body></html>")
    result = scraper.scrape("https://www.delish.com/cooking/recipe-ideas/a2/minimal/")

    assert result.title == "Minimal"
    assert result.description == ""
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time == ""
    assert result.cook_time == ""
    assert result.servings == ""
