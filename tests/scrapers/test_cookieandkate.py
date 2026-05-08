"""Tests for the Cookie and Kate scraper."""
from unittest.mock import MagicMock, patch

import pytest

from reciparse.scrapers.cookieandkate import CookieAndKateScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture
def scraper():
    return CookieAndKateScraper()


def _make_mock_response(html: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


_SAMPLE_HTML = """
<html><body>
  <h2 class="wprm-recipe-name">Honey Whole Wheat Bread</h2>
  <div class="wprm-recipe-summary">A wholesome loaf perfect for any day.</div>
  <ul>
    <li class="wprm-recipe-ingredient">2 cups whole wheat flour</li>
    <li class="wprm-recipe-ingredient">1 tbsp honey</li>
    <li class="wprm-recipe-ingredient">1 tsp salt</li>
  </ul>
  <div class="wprm-recipe-instruction-text">Mix dry ingredients.</div>
  <div class="wprm-recipe-instruction-text">Add wet ingredients and knead.</div>
  <span class="wprm-recipe-prep_time-container">15 mins</span>
  <span class="wprm-recipe-cook_time-container">30 mins</span>
  <span class="wprm-recipe-servings-container">12 slices</span>
</body></html>
"""


def test_supports_cookieandkate_url(scraper):
    assert scraper.supports("https://cookieandkate.com/honey-whole-wheat-bread/")


def test_supports_cookieandkate_no_www(scraper):
    assert scraper.supports("https://www.cookieandkate.com/some-recipe/")


def test_does_not_support_other_url(scraper):
    assert not scraper.supports("https://allrecipes.com/recipe/12345/")


def test_scrape_returns_recipe_data(scraper):
    with patch("reciparse.scrapers.cookieandkate.requests.get") as mock_get:
        mock_get.return_value = _make_mock_response(_SAMPLE_HTML)
        result = scraper.scrape("https://cookieandkate.com/honey-whole-wheat-bread/")

    assert isinstance(result, RecipeData)
    assert result.title == "Honey Whole Wheat Bread"
    assert result.description == "A wholesome loaf perfect for any day."
    assert len(result.ingredients) == 3
    assert "2 cups whole wheat flour" in result.ingredients
    assert len(result.instructions) == 2
    assert result.prep_time == "15 mins"
    assert result.cook_time == "30 mins"
    assert result.servings == "12 slices"
    assert result.url == "https://cookieandkate.com/honey-whole-wheat-bread/"


def test_scrape_handles_missing_fields(scraper):
    html = "<html><body><h1 class='entry-title'>Simple Salad</h1></body></html>"
    with patch("reciparse.scrapers.cookieandkate.requests.get") as mock_get:
        mock_get.return_value = _make_mock_response(html)
        result = scraper.scrape("https://cookieandkate.com/simple-salad/")

    assert result.title == "Simple Salad"
    assert result.description == ""
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time == ""
    assert result.cook_time == ""
    assert result.servings == ""
