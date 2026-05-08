import pytest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup

from reciparse.scrapers.thepioneerwoman import ThePioneerWomanScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture
def scraper():
    return ThePioneerWomanScraper()


def _make_mock_response(html: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


FULL_HTML = """
<html>
  <head>
    <meta property="og:title" content="Pioneer Skillet" />
    <meta name="description" content="A hearty skillet meal." />
  </head>
  <body>
    <h1 class="recipe-title">Pioneer Skillet</h1>
    <div class="recipe-description">A hearty skillet meal.</div>
    <ul class="ingredients-list">
      <li>2 cups flour</li>
      <li>1 tsp salt</li>
    </ul>
    <ol class="directions-list">
      <li>Mix dry ingredients.</li>
      <li>Cook on medium heat.</li>
    </ol>
    <span data-label="Prep Time">15 mins</span>
    <span data-label="Cook Time">30 mins</span>
    <span data-label="Servings">4</span>
  </body>
</html>
"""

EMPTY_HTML = "<html><body></body></html>"


def test_supports_thepioneerwoman_url(scraper):
    assert scraper.supports("https://www.thepioneerwoman.com/food-cooking/recipes/a123/pioneer-skillet/")


def test_supports_thepioneerwoman_no_www(scraper):
    assert scraper.supports("https://thepioneerwoman.com/food-cooking/recipes/a123/pioneer-skillet/")


def test_does_not_support_other_url(scraper):
    assert not scraper.supports("https://www.allrecipes.com/recipe/12345/")


@patch("reciparse.scrapers.thepioneerwoman.requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_get.return_value = _make_mock_response(FULL_HTML)
    result = scraper.scrape("https://www.thepioneerwoman.com/food-cooking/recipes/a123/pioneer-skillet/")
    assert isinstance(result, RecipeData)
    assert result.title == "Pioneer Skillet"
    assert result.description == "A hearty skillet meal."
    assert "2 cups flour" in result.ingredients
    assert "1 tsp salt" in result.ingredients
    assert "Mix dry ingredients." in result.instructions
    assert "Cook on medium heat." in result.instructions


@patch("reciparse.scrapers.thepioneerwoman.requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_get.return_value = _make_mock_response(EMPTY_HTML)
    result = scraper.scrape("https://www.thepioneerwoman.com/food-cooking/recipes/a123/empty/")
    assert isinstance(result, RecipeData)
    assert result.title == ""
    assert result.ingredients == []
    assert result.instructions == []


@patch("reciparse.scrapers.thepioneerwoman.requests.get")
def test_scrape_source_url_set(mock_get, scraper):
    url = "https://www.thepioneerwoman.com/food-cooking/recipes/a123/pioneer-skillet/"
    mock_get.return_value = _make_mock_response(FULL_HTML)
    result = scraper.scrape(url)
    assert result.source_url == url
