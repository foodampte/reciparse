"""Tests for the 101cookbooks.com scraper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from reciparse.scrapers["101cookbooks"] import HundredAndOneCookbooksScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture()
def scraper() -> HundredAndOneCookbooksScraper:
    return HundredAndOneCookbooksScraper()


def _make_mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


def test_supports_101cookbooks_url(scraper):
    assert scraper.supports("https://www.101cookbooks.com/lentil-soup/") is True


def test_supports_101cookbooks_no_www(scraper):
    assert scraper.supports("https://101cookbooks.com/pasta-recipe/") is True


def test_does_not_support_other_url(scraper):
    assert scraper.supports("https://www.allrecipes.com/recipe/123/") is False


_SAMPLE_HTML = """
<html>
  <body>
    <h1>Simple Lentil Soup</h1>
    <div class="recipe-description">A hearty and warming soup.</div>
    <ul class="ingredients-list">
      <li>1 cup red lentils</li>
      <li>2 cloves garlic</li>
    </ul>
    <ol class="instructions-list">
      <li>Rinse the lentils.</li>
      <li>Simmer for 20 minutes.</li>
    </ol>
    <span class="prep-time">10 minutes</span>
    <span class="cook-time">25 minutes</span>
    <span class="servings">4 servings</span>
  </body>
</html>
"""


@patch("reciparse.scrapers['101cookbooks'].requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_get.return_value = _make_mock_response(_SAMPLE_HTML)
    result = scraper.scrape("https://101cookbooks.com/lentil-soup/")
    assert isinstance(result, RecipeData)
    assert result.title == "Simple Lentil Soup"
    assert "1 cup red lentils" in result.ingredients
    assert "Rinse the lentils." in result.instructions
    assert result.servings == "4 servings"


@patch("reciparse.scrapers['101cookbooks'].requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_get.return_value = _make_mock_response("<html><body><h1>Bare Recipe</h1></body></html>")
    result = scraper.scrape("https://101cookbooks.com/bare/")
    assert result.title == "Bare Recipe"
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time == ""
    assert result.cook_time == ""
