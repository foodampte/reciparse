import pytest
from unittest.mock import MagicMock, patch

from reciparse.scrapers.bonappetit import BonAppetitScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture
def scraper():
    return BonAppetitScraper()


def test_supports_bonappetit_url(scraper):
    assert scraper.supports("https://www.bonappetit.com/recipe/pasta-primavera") is True


def test_supports_bonappetit_no_www(scraper):
    assert scraper.supports("https://bonappetit.com/recipe/pasta-primavera") is True


def test_does_not_support_other_url(scraper):
    assert scraper.supports("https://www.allrecipes.com/recipe/12345") is False


def _make_mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


FULL_HTML = """
<html><body>
  <h1 data-testid="ContentHeaderHed">Pasta Primavera</h1>
  <div class="dek">A fresh spring pasta dish.</div>
  <div data-testid="IngredientList">2 cups pasta</div>
  <div data-testid="IngredientList">1 cup vegetables</div>
  <p class="step">Boil water and cook pasta.</p>
  <p class="step">Saute vegetables and combine.</p>
  <span itemprop="prepTime">15 minutes</span>
  <span itemprop="cookTime">20 minutes</span>
  <span itemprop="recipeYield">4 servings</span>
</body></html>
"""


@patch("reciparse.scrapers.bonappetit.requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_get.return_value = _make_mock_response(FULL_HTML)
    url = "https://www.bonappetit.com/recipe/pasta-primavera"
    result = scraper.scrape(url)

    assert isinstance(result, RecipeData)
    assert result.title == "Pasta Primavera"
    assert result.description == "A fresh spring pasta dish."
    assert len(result.ingredients) == 2
    assert len(result.instructions) == 2
    assert result.prep_time == "15 minutes"
    assert result.cook_time == "20 minutes"
    assert result.servings == "4 servings"
    assert result.source_url == url


EMPTY_HTML = "<html><body></body></html>"


@patch("reciparse.scrapers.bonappetit.requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_get.return_value = _make_mock_response(EMPTY_HTML)
    result = scraper.scrape("https://www.bonappetit.com/recipe/mystery")

    assert isinstance(result, RecipeData)
    assert result.title is None
    assert result.description is None
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time is None
    assert result.cook_time is None
    assert result.servings is None


@patch("reciparse.scrapers.bonappetit.requests.get")
def test_scrape_uses_og_title_fallback(mock_get, scraper):
    html = '<html><head><meta property="og:title" content="OG Pasta"/></head><body></body></html>'
    mock_get.return_value = _make_mock_response(html)
    result = scraper.scrape("https://www.bonappetit.com/recipe/og-pasta")
    assert result.title == "OG Pasta"
