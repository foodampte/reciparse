"""Tests for the HalfBakedHarvestScraper."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from reciparse.scrapers.halfbakedharvest import HalfBakedHarvestScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture
def scraper() -> HalfBakedHarvestScraper:
    return HalfBakedHarvestScraper()


def _make_mock_response(html: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


_SAMPLE_HTML = """
<html><body>
  <h2 class="wprm-recipe-name">Lemon Pasta</h2>
  <div class="wprm-recipe-summary">A bright, lemony pasta dish.</div>
  <ul>
    <li class="wprm-recipe-ingredient">200g spaghetti</li>
    <li class="wprm-recipe-ingredient">1 lemon, zested</li>
  </ul>
  <div class="wprm-recipe-instruction-text">Boil pasta until al dente.</div>
  <div class="wprm-recipe-instruction-text">Toss with lemon zest and olive oil.</div>
  <span class="wprm-recipe-prep-time-container">
    <span class="wprm-recipe-prep_time-minutes">10</span>
  </span>
  <span class="wprm-recipe-cook-time-container">
    <span class="wprm-recipe-cook_time-minutes">15</span>
  </span>
  <span class="wprm-recipe-servings">4</span>
</body></html>
"""


def test_supports_halfbakedharvest_url(scraper):
    assert scraper.supports("https://www.halfbakedharvest.com/lemon-pasta/")


def test_supports_halfbakedharvest_no_www(scraper):
    assert scraper.supports("https://halfbakedharvest.com/lemon-pasta/")


def test_does_not_support_other_url(scraper):
    assert not scraper.supports("https://www.allrecipes.com/recipe/123/")


@patch("reciparse.scrapers.halfbakedharvest.requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_get.return_value = _make_mock_response(_SAMPLE_HTML)
    result = scraper.scrape("https://www.halfbakedharvest.com/lemon-pasta/")

    assert isinstance(result, RecipeData)
    assert result.title == "Lemon Pasta"
    assert result.description == "A bright, lemony pasta dish."
    assert "200g spaghetti" in result.ingredients
    assert "1 lemon, zested" in result.ingredients
    assert len(result.instructions) == 2
    assert result.prep_time == "10 minutes"
    assert result.cook_time == "15 minutes"
    assert result.servings == "4"
    assert result.source_url == "https://www.halfbakedharvest.com/lemon-pasta/"


@patch("reciparse.scrapers.halfbakedharvest.requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_get.return_value = _make_mock_response("<html><body></body></html>")
    result = scraper.scrape("https://www.halfbakedharvest.com/empty/")

    assert isinstance(result, RecipeData)
    assert result.title == ""
    assert result.description == ""
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time == ""
    assert result.cook_time == ""
    assert result.servings == ""
