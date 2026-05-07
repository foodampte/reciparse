import pytest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup

from reciparse.scrapers.kingarthurbaking import KingArthurBakingScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture
def scraper():
    return KingArthurBakingScraper()


def _make_mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


SAMPLE_HTML = """
<html><body>
  <h1 class="recipe-title">Classic Sourdough Bread</h1>
  <div class="recipe-description">A tangy, chewy loaf with a crisp crust.</div>
  <ul class="ingredients-list">
    <li>500g bread flour</li>
    <li>375ml water</li>
    <li>10g salt</li>
    <li>100g active starter</li>
  </ul>
  <ol class="instructions-list">
    <li>Mix flour and water; autolyse for 30 minutes.</li>
    <li>Add starter and salt; fold every 30 minutes for 3 hours.</li>
    <li>Shape and cold-proof overnight.</li>
    <li>Bake at 500°F for 20 minutes covered, then 25 minutes uncovered.</li>
  </ol>
  <span class="prep-time" data-time-type="prep">30 mins</span>
  <span class="bake-time" data-time-type="bake">45 mins</span>
  <span class="yield">1 loaf</span>
</body></html>
"""

MINIMAL_HTML = "<html><body><h1>Plain Bread</h1></body></html>"


def test_supports_kingarthurbaking_url(scraper):
    assert scraper.supports("https://www.kingarthurbaking.com/recipes/sourdough") is True


def test_supports_kingarthurbaking_no_www(scraper):
    assert scraper.supports("https://kingarthurbaking.com/recipes/sourdough") is True


def test_does_not_support_other_url(scraper):
    assert scraper.supports("https://www.allrecipes.com/recipe/123") is False


@patch("reciparse.scrapers.kingarthurbaking.requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_get.return_value = _make_mock_response(SAMPLE_HTML)
    url = "https://www.kingarthurbaking.com/recipes/classic-sourdough"
    result = scraper.scrape(url)

    assert isinstance(result, RecipeData)
    assert result.title == "Classic Sourdough Bread"
    assert result.description == "A tangy, chewy loaf with a crisp crust."
    assert len(result.ingredients) == 4
    assert "500g bread flour" in result.ingredients
    assert len(result.instructions) == 4
    assert result.prep_time == "30 mins"
    assert result.cook_time == "45 mins"
    assert result.servings == "1 loaf"
    assert result.url == url


@patch("reciparse.scrapers.kingarthurbaking.requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_get.return_value = _make_mock_response(MINIMAL_HTML)
    result = scraper.scrape("https://www.kingarthurbaking.com/recipes/plain")

    assert isinstance(result, RecipeData)
    assert result.title == "Plain Bread"
    assert result.description == ""
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time == ""
    assert result.cook_time == ""
    assert result.servings == ""


@patch("reciparse.scrapers.kingarthurbaking.requests.get")
def test_scrape_calls_correct_url(mock_get, scraper):
    mock_get.return_value = _make_mock_response(MINIMAL_HTML)
    url = "https://www.kingarthurbaking.com/recipes/focaccia"
    scraper.scrape(url)
    mock_get.assert_called_once_with(url, timeout=10)
