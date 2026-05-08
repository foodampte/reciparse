import pytest
from unittest.mock import MagicMock, patch

from reciparse.scrapers.loveandlemons import LoveAndLemonsScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture
def scraper():
    return LoveAndLemonsScraper()


def _make_mock_response(html: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


FULL_HTML = """
<html>
  <head>
    <meta property="og:title" content="Lemon Pasta" />
    <meta name="description" content="Bright and zesty pasta." />
  </head>
  <body>
    <h2 class="wprm-recipe-name">Lemon Pasta</h2>
    <div class="wprm-recipe-summary">Bright and zesty pasta.</div>
    <li class="wprm-recipe-ingredient">200g spaghetti</li>
    <li class="wprm-recipe-ingredient">1 lemon, zested</li>
    <div class="wprm-recipe-instruction-text">Boil pasta until al dente.</div>
    <div class="wprm-recipe-instruction-text">Toss with lemon zest and olive oil.</div>
    <span class="wprm-recipe-prep_time-container">10 minutes</span>
    <span class="wprm-recipe-cook_time-container">15 minutes</span>
    <span class="wprm-recipe-servings-container">2 servings</span>
  </body>
</html>
"""

EMPTY_HTML = "<html><body></body></html>"


def test_supports_loveandlemons_url(scraper):
    assert scraper.supports("https://www.loveandlemons.com/lemon-pasta/")


def test_supports_loveandlemons_no_www(scraper):
    assert scraper.supports("https://loveandlemons.com/lemon-pasta/")


def test_does_not_support_other_url(scraper):
    assert not scraper.supports("https://www.allrecipes.com/recipe/12345/")


@patch("reciparse.scrapers.loveandlemons.requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_get.return_value = _make_mock_response(FULL_HTML)
    result = scraper.scrape("https://www.loveandlemons.com/lemon-pasta/")
    assert isinstance(result, RecipeData)
    assert result.title == "Lemon Pasta"
    assert result.description == "Bright and zesty pasta."
    assert "200g spaghetti" in result.ingredients
    assert "1 lemon, zested" in result.ingredients
    assert "Boil pasta until al dente." in result.instructions


@patch("reciparse.scrapers.loveandlemons.requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_get.return_value = _make_mock_response(EMPTY_HTML)
    result = scraper.scrape("https://www.loveandlemons.com/empty/")
    assert isinstance(result, RecipeData)
    assert result.title == ""
    assert result.ingredients == []
    assert result.instructions == []


@patch("reciparse.scrapers.loveandlemons.requests.get")
def test_scrape_source_url_set(mock_get, scraper):
    url = "https://www.loveandlemons.com/lemon-pasta/"
    mock_get.return_value = _make_mock_response(FULL_HTML)
    result = scraper.scrape(url)
    assert result.source_url == url
