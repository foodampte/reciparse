from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from reciparse.scrapers.thekitchn import TheKitchnScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture
def scraper():
    return TheKitchnScraper()


def _make_mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


def test_supports_thekitchn_url(scraper):
    assert scraper.supports("https://www.thekitchn.com/recipe/pasta") is True


def test_supports_thekitchn_no_www(scraper):
    assert scraper.supports("https://thekitchn.com/recipe/pasta") is True


def test_does_not_support_other_url(scraper):
    assert scraper.supports("https://www.allrecipes.com/recipe/123") is False


FULL_HTML = """
<html><body>
  <h1 class="Recipe__title">Lemon Pasta</h1>
  <div class="Recipe__description">A bright and zesty pasta dish.</div>
  <ul class="Recipe__ingredients">
    <li>200g spaghetti</li>
    <li>1 lemon, zested and juiced</li>
    <li>2 tbsp olive oil</li>
  </ul>
  <ol class="Recipe__instructions">
    <li>Cook spaghetti according to package directions.</li>
    <li>Toss with lemon juice, zest, and olive oil.</li>
  </ol>
  <span data-recipe-time-type="prep">10 mins</span>
  <span data-recipe-time-type="cook">15 mins</span>
  <span data-recipe-servings="4">4</span>
</body></html>
"""

EMPTY_HTML = "<html><body></body></html>"


@patch("reciparse.scrapers.thekitchn.requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_get.return_value = _make_mock_response(FULL_HTML)
    result = scraper.scrape("https://www.thekitchn.com/recipe/lemon-pasta")

    assert isinstance(result, RecipeData)
    assert result.title == "Lemon Pasta"
    assert result.description == "A bright and zesty pasta dish."
    assert len(result.ingredients) == 3
    assert "200g spaghetti" in result.ingredients
    assert len(result.instructions) == 2
    assert result.prep_time == "10 mins"
    assert result.cook_time == "15 mins"
    assert result.servings == "4"
    assert result.url == "https://www.thekitchn.com/recipe/lemon-pasta"


@patch("reciparse.scrapers.thekitchn.requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_get.return_value = _make_mock_response(EMPTY_HTML)
    result = scraper.scrape("https://www.thekitchn.com/recipe/unknown")

    assert isinstance(result, RecipeData)
    assert result.title is None
    assert result.description is None
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time is None
    assert result.cook_time is None
    assert result.servings is None


@patch("reciparse.scrapers.thekitchn.requests.get")
def test_scrape_url_stored_on_result(mock_get, scraper):
    mock_get.return_value = _make_mock_response(FULL_HTML)
    url = "https://www.thekitchn.com/recipe/lemon-pasta"
    result = scraper.scrape(url)
    assert result.url == url
