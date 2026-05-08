import pytest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup

from reciparse.scrapers.skinnytaste import SkinnyTasteScraper
from reciparse.scrapers.base import RecipeData


SAMPLE_URL = "https://www.skinnytaste.com/chicken-soup/"

SAMPLE_HTML = """
<html><body>
  <h2 class="wprm-recipe-name">Healthy Chicken Soup</h2>
  <div class="wprm-recipe-summary">A light and nourishing soup.</div>
  <ul>
    <li class="wprm-recipe-ingredient">2 cups chicken broth</li>
    <li class="wprm-recipe-ingredient">1 cup shredded chicken</li>
    <li class="wprm-recipe-ingredient">1 carrot, sliced</li>
  </ul>
  <div class="wprm-recipe-instruction-text">Bring broth to a boil.</div>
  <div class="wprm-recipe-instruction-text">Add chicken and carrot. Simmer 15 min.</div>
  <span class="wprm-recipe-prep_time-container">10 mins</span>
  <span class="wprm-recipe-cook_time-container">20 mins</span>
  <span class="wprm-recipe-servings-container">4 servings</span>
</body></html>
"""


@pytest.fixture
def scraper():
    return SkinnyTasteScraper()


def _make_mock_response(html: str = SAMPLE_HTML):
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def test_supports_skinnytaste_url(scraper):
    assert scraper.supports("https://www.skinnytaste.com/chicken-soup/") is True


def test_supports_skinnytaste_no_www(scraper):
    assert scraper.supports("https://skinnytaste.com/chicken-soup/") is True


def test_does_not_support_other_url(scraper):
    assert scraper.supports("https://allrecipes.com/recipe/123") is False


@patch("reciparse.scrapers.skinnytaste.requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_get.return_value = _make_mock_response()
    result = scraper.scrape(SAMPLE_URL)
    assert isinstance(result, RecipeData)
    assert result.title == "Healthy Chicken Soup"
    assert result.description == "A light and nourishing soup."
    assert len(result.ingredients) == 3
    assert "chicken broth" in result.ingredients[0]
    assert len(result.instructions) == 2
    assert result.prep_time == "10 mins"
    assert result.cook_time == "20 mins"
    assert result.servings == "4 servings"
    assert result.source_url == SAMPLE_URL


@patch("reciparse.scrapers.skinnytaste.requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_get.return_value = _make_mock_response("<html><body></body></html>")
    result = scraper.scrape(SAMPLE_URL)
    assert result.title == ""
    assert result.description == ""
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time == ""
    assert result.cook_time == ""
    assert result.servings == ""
