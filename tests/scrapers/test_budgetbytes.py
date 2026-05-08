import pytest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup

from reciparse.scrapers.budgetbytes import BudgetBytesScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture
def scraper():
    return BudgetBytesScraper()


DUMMY_HTML = """
<html><body>
  <h1 class="wprm-recipe-name">Chicken Fried Rice</h1>
  <div class="wprm-recipe-summary">A quick and easy weeknight dinner.</div>
  <ul>
    <li class="wprm-recipe-ingredient">2 cups cooked rice</li>
    <li class="wprm-recipe-ingredient">1 cup frozen peas</li>
    <li class="wprm-recipe-ingredient">2 eggs</li>
  </ul>
  <ul>
    <li><span class="wprm-recipe-instruction-text">Heat oil in a pan.</span></li>
    <li><span class="wprm-recipe-instruction-text">Add rice and stir-fry.</span></li>
  </ul>
  <span class="wprm-recipe-prep-time-container">10 mins</span>
  <span class="wprm-recipe-cook-time-container">15 mins</span>
  <span class="wprm-recipe-servings-with-unit">4 servings</span>
</body></html>
"""


def _make_mock_response(html: str = DUMMY_HTML) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


def test_supports_budgetbytes_url(scraper):
    assert scraper.supports("https://www.budgetbytes.com/chicken-fried-rice/")


def test_supports_budgetbytes_no_www(scraper):
    assert scraper.supports("https://budgetbytes.com/chicken-fried-rice/")


def test_does_not_support_other_url(scraper):
    assert not scraper.supports("https://www.allrecipes.com/recipe/12345/")


@patch("reciparse.scrapers.budgetbytes.requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_get.return_value = _make_mock_response()
    result = scraper.scrape("https://www.budgetbytes.com/chicken-fried-rice/")

    assert isinstance(result, RecipeData)
    assert result.title == "Chicken Fried Rice"
    assert result.description == "A quick and easy weeknight dinner."
    assert len(result.ingredients) == 3
    assert "cooked rice" in result.ingredients[0]
    assert len(result.instructions) == 2
    assert result.prep_time == "10 mins"
    assert result.cook_time == "15 mins"
    assert result.servings == "4 servings"
    assert result.url == "https://www.budgetbytes.com/chicken-fried-rice/"


@patch("reciparse.scrapers.budgetbytes.requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_get.return_value = _make_mock_response("<html><body></body></html>")
    result = scraper.scrape("https://www.budgetbytes.com/empty/")

    assert isinstance(result, RecipeData)
    assert result.title == ""
    assert result.description == ""
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time == ""
    assert result.cook_time == ""
    assert result.servings == ""
