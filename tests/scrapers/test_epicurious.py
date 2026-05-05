"""Tests for the Epicurious scraper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from reciparse.scrapers.base import RecipeData
from reciparse.scrapers.epicurious import EpicuriousScraper


@pytest.fixture()
def scraper() -> EpicuriousScraper:
    return EpicuriousScraper()


def test_supports_epicurious_url(scraper):
    assert scraper.supports("https://www.epicurious.com/recipes/food/views/pasta")


def test_supports_epicurious_no_www(scraper):
    assert scraper.supports("https://epicurious.com/recipes/food/views/pasta")


def test_does_not_support_other_url(scraper):
    assert not scraper.supports("https://www.allrecipes.com/recipe/12345")


def _make_mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


_SAMPLE_HTML = """
<html><body>
  <h1 data-testid="recipe-title">Lemon Pasta</h1>
  <div class="dek">A bright, simple pasta dish.</div>
  <li data-testid="IngredientList">200g pasta</li>
  <li data-testid="IngredientList">1 lemon, zested</li>
  <li class="step">Boil pasta until al dente.</li>
  <li class="step">Toss with lemon zest and olive oil.</li>
  <span itemprop="preptime" datetime="PT10M">10 mins</span>
  <span itemprop="cooktime" datetime="PT20M">20 mins</span>
  <span itemprop="recipeYield">2 servings</span>
</body></html>
"""


@patch("reciparse.scrapers.epicurious.requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_get.return_value = _make_mock_response(_SAMPLE_HTML)
    url = "https://www.epicurious.com/recipes/food/views/lemon-pasta"
    result = scraper.scrape(url)

    assert isinstance(result, RecipeData)
    assert result.title == "Lemon Pasta"
    assert result.description == "A bright, simple pasta dish."
    assert len(result.ingredients) == 2
    assert "200g pasta" in result.ingredients
    assert len(result.instructions) == 2
    assert result.prep_time == "PT10M"
    assert result.cook_time == "PT20M"
    assert result.servings == "2 servings"
    assert result.source_url == url


_MINIMAL_HTML = "<html><body><h1>Plain Recipe</h1></body></html>"


@patch("reciparse.scrapers.epicurious.requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_get.return_value = _make_mock_response(_MINIMAL_HTML)
    result = scraper.scrape("https://www.epicurious.com/recipes/food/views/plain")

    assert result.title == "Plain Recipe"
    assert result.description is None
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time is None
    assert result.cook_time is None
    assert result.servings is None
