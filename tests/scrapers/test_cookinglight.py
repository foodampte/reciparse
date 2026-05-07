"""Tests for the CookingLight scraper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from reciparse.scrapers.cookinglight import CookingLightScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture
def scraper() -> CookingLightScraper:
    return CookingLightScraper()


def test_supports_cookinglight_url(scraper):
    assert scraper.supports("https://www.cookinglight.com/recipes/chicken-soup")


def test_supports_cookinglight_no_www(scraper):
    assert scraper.supports("https://cookinglight.com/recipes/chicken-soup")


def test_does_not_support_other_url(scraper):
    assert not scraper.supports("https://www.allrecipes.com/recipe/123")


def _make_mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


_FULL_HTML = """
<html><body>
  <h1 class="recipe-title">Lemon Herb Chicken</h1>
  <div class="recipe-summary">A bright and healthy weeknight dinner.</div>
  <ul class="ingredients-section">
    <li>2 chicken breasts</li>
    <li>1 lemon, zested</li>
    <li>2 tbsp olive oil</li>
  </ul>
  <ol class="instructions-section">
    <li>Preheat oven to 400F.</li>
    <li>Season chicken and roast 25 minutes.</li>
  </ol>
  <div class="recipe-meta-item">Prep Time: 10 mins</div>
  <div class="recipe-meta-item">Cook Time: 25 mins</div>
  <div class="recipe-meta-item">Servings: 2</div>
</body></html>
"""


@patch("reciparse.scrapers.cookinglight.requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_get.return_value = _make_mock_response(_FULL_HTML)
    result = scraper.scrape("https://www.cookinglight.com/recipes/lemon-herb-chicken")

    assert isinstance(result, RecipeData)
    assert result.title == "Lemon Herb Chicken"
    assert result.description == "A bright and healthy weeknight dinner."
    assert len(result.ingredients) == 3
    assert "chicken breasts" in result.ingredients[0]
    assert len(result.instructions) == 2
    assert result.source_url == "https://www.cookinglight.com/recipes/lemon-herb-chicken"


_MINIMAL_HTML = """
<html><body>
  <meta property="og:title" content="Simple Salad" />
  <meta name="description" content="A quick salad." />
</body></html>
"""


@patch("reciparse.scrapers.cookinglight.requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_get.return_value = _make_mock_response(_MINIMAL_HTML)
    result = scraper.scrape("https://cookinglight.com/recipes/simple-salad")

    assert result.title == "Simple Salad"
    assert result.description == "A quick salad."
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time == ""
    assert result.cook_time == ""
    assert result.servings == ""


@patch("reciparse.scrapers.cookinglight.requests.get")
def test_scrape_passes_url_as_source(mock_get, scraper):
    mock_get.return_value = _make_mock_response(_MINIMAL_HTML)
    url = "https://cookinglight.com/recipes/test"
    result = scraper.scrape(url)
    assert result.source_url == url
