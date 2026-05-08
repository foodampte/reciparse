"""Tests for the SmittenKitchen scraper."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from reciparse.scrapers.smittenkitchen import SmittenKitchenScraper


@pytest.fixture()
def scraper() -> SmittenKitchenScraper:
    return SmittenKitchenScraper()


def _make_mock_response(html: str) -> MagicMock:
    mock = MagicMock()
    mock.text = html
    mock.raise_for_status = MagicMock()
    return mock


# ---------------------------------------------------------------------------
# supports()
# ---------------------------------------------------------------------------

def test_supports_smittenkitchen_url(scraper):
    assert scraper.supports("https://smittenkitchen.com/2023/01/some-recipe/") is True


def test_supports_smittenkitchen_no_www(scraper):
    assert scraper.supports("https://www.smittenkitchen.com/recipe/cake") is True


def test_does_not_support_other_url(scraper):
    assert scraper.supports("https://allrecipes.com/recipe/123") is False


# ---------------------------------------------------------------------------
# scrape()
# ---------------------------------------------------------------------------

_FULL_HTML = """
<html><head>
  <meta name="description" content="A rich chocolate cake." />
</head><body>
  <h1 class="entry-title">Chocolate Cake</h1>
  <div class="entry-content">
    <p>Best cake ever.</p>
    <ul class="ingredients-list">
      <li>2 cups flour</li>
      <li>1 cup sugar</li>
    </ul>
    <ol class="instructions">
      <li>Mix dry ingredients.</li>
      <li>Bake at 350F for 30 min.</li>
    </ol>
    <span class="prep-time">Prep: 15 minutes</span>
    <span class="cook-time">Cook: 30 minutes</span>
    <span class="servings">Serves 8</span>
  </div>
</body></html>
"""


@pytest.fixture()
def mock_full_response():
    return _make_mock_response(_FULL_HTML)


def test_scrape_returns_recipe_data(scraper, mock_full_response):
    with patch("reciparse.scrapers.smittenkitchen.requests.get", return_value=mock_full_response):
        result = scraper.scrape("https://smittenkitchen.com/2023/01/chocolate-cake/")
    assert result.title == "Chocolate Cake"
    assert result.description == "A rich chocolate cake."
    assert "2 cups flour" in result.ingredients
    assert "1 cup sugar" in result.ingredients
    assert result.instructions[0] == "Mix dry ingredients."
    assert result.prep_time == "15 minutes"
    assert result.cook_time == "30 minutes"
    assert result.servings == "8"


def test_scrape_handles_missing_fields(scraper):
    html = "<html><body><h1>Simple Recipe</h1></body></html>"
    mock_resp = _make_mock_response(html)
    with patch("reciparse.scrapers.smittenkitchen.requests.get", return_value=mock_resp):
        result = scraper.scrape("https://smittenkitchen.com/2023/01/simple/")
    assert result.title == "Simple Recipe"
    assert result.description == ""
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time is None
    assert result.cook_time is None
    assert result.servings is None
