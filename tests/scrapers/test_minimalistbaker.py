from unittest.mock import MagicMock, patch

import pytest

from reciparse.scrapers.minimalistbaker import MinimalistBakerScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture
def scraper():
    return MinimalistBakerScraper()


def _make_mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


def test_supports_minimalistbaker_url(scraper):
    assert scraper.supports("https://minimalistbaker.com/easy-vegan-pancakes/")


def test_supports_minimalistbaker_no_www(scraper):
    assert scraper.supports("https://www.minimalistbaker.com/easy-vegan-pancakes/")


def test_does_not_support_other_url(scraper):
    assert not scraper.supports("https://allrecipes.com/recipe/12345")


MINIMAL_HTML = """
<html><body>
  <h2 class="wprm-recipe-name">Simple Pancakes</h2>
  <div class="wprm-recipe-summary">Fluffy and delicious.</div>
  <li class="wprm-recipe-ingredient">1 cup flour</li>
  <li class="wprm-recipe-ingredient">1 tbsp sugar</li>
  <div class="wprm-recipe-instruction-text">Mix dry ingredients.</div>
  <div class="wprm-recipe-instruction-text">Cook on griddle.</div>
  <span class="wprm-recipe-prep_time-container">5 mins</span>
  <span class="wprm-recipe-cook_time-container">10 mins</span>
  <span class="wprm-recipe-servings-container">4 servings</span>
</body></html>
"""


@patch("reciparse.scrapers.minimalistbaker.requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_get.return_value = _make_mock_response(MINIMAL_HTML)
    result = scraper.scrape("https://minimalistbaker.com/simple-pancakes/")
    assert isinstance(result, RecipeData)


@patch("reciparse.scrapers.minimalistbaker.requests.get")
def test_scrape_parses_title(mock_get, scraper):
    mock_get.return_value = _make_mock_response(MINIMAL_HTML)
    result = scraper.scrape("https://minimalistbaker.com/simple-pancakes/")
    assert result.title == "Simple Pancakes"


@patch("reciparse.scrapers.minimalistbaker.requests.get")
def test_scrape_parses_ingredients(mock_get, scraper):
    mock_get.return_value = _make_mock_response(MINIMAL_HTML)
    result = scraper.scrape("https://minimalistbaker.com/simple-pancakes/")
    assert len(result.ingredients) == 2
    assert "flour" in result.ingredients[0]


@patch("reciparse.scrapers.minimalistbaker.requests.get")
def test_scrape_parses_instructions(mock_get, scraper):
    mock_get.return_value = _make_mock_response(MINIMAL_HTML)
    result = scraper.scrape("https://minimalistbaker.com/simple-pancakes/")
    assert len(result.instructions) == 2


@patch("reciparse.scrapers.minimalistbaker.requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_get.return_value = _make_mock_response("<html><body></body></html>")
    result = scraper.scrape("https://minimalistbaker.com/simple-pancakes/")
    assert result.title == ""
    assert result.ingredients == []
    assert result.instructions == []
