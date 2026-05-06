"""Tests for the TastyScraper."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from reciparse.scrapers.tasty import TastyScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture()
def scraper() -> TastyScraper:
    return TastyScraper()


def _make_mock_response(html: str) -> MagicMock:
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


def test_supports_tasty_url(scraper: TastyScraper) -> None:
    assert scraper.supports("https://tasty.co/recipe/classic-pancakes") is True


def test_supports_tasty_no_www(scraper: TastyScraper) -> None:
    assert scraper.supports("https://tasty.co/recipe/banana-bread") is True


def test_does_not_support_other_url(scraper: TastyScraper) -> None:
    assert scraper.supports("https://allrecipes.com/recipe/123") is False
    assert scraper.supports("https://notatasty.co/recipe/abc") is False


_FULL_HTML = """
<html>
  <head>
    <meta property="og:title" content="OG Title" />
    <meta property="og:description" content="OG Desc" />
  </head>
  <body>
    <h1 class="recipe-name">Classic Pancakes</h1>
    <p class="description">Fluffy and delicious.</p>
    <ul class="ingredients">
      <li>1 cup flour</li>
      <li>2 eggs</li>
      <li>1 cup milk</li>
    </ul>
    <ol class="prep-steps">
      <li>Mix dry ingredients.</li>
      <li>Add wet ingredients and stir.</li>
      <li>Cook on griddle.</li>
    </ol>
    <dd class="prep-time">10 mins</dd>
    <dd class="cook-time">15 mins</dd>
    <dd class="servings">4</dd>
  </body>
</html>
"""


@patch("reciparse.scrapers.tasty.requests.get")
def test_scrape_returns_recipe_data(mock_get: MagicMock, scraper: TastyScraper) -> None:
    mock_get.return_value = _make_mock_response(_FULL_HTML)
    result = scraper.scrape("https://tasty.co/recipe/classic-pancakes")

    assert isinstance(result, RecipeData)
    assert result.title == "Classic Pancakes"
    assert result.description == "Fluffy and delicious."
    assert result.ingredients == ["1 cup flour", "2 eggs", "1 cup milk"]
    assert len(result.instructions) == 3
    assert result.prep_time == "10 mins"
    assert result.cook_time == "15 mins"
    assert result.servings == "4"
    assert result.url == "https://tasty.co/recipe/classic-pancakes"


@patch("reciparse.scrapers.tasty.requests.get")
def test_scrape_handles_missing_fields(mock_get: MagicMock, scraper: TastyScraper) -> None:
    mock_get.return_value = _make_mock_response("<html><body></body></html>")
    result = scraper.scrape("https://tasty.co/recipe/empty")

    assert result.title == ""
    assert result.description == ""
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time == ""
    assert result.cook_time == ""
    assert result.servings == ""


@patch("reciparse.scrapers.tasty.requests.get")
def test_scrape_falls_back_to_og_tags(mock_get: MagicMock, scraper: TastyScraper) -> None:
    html = (
        '<html><head>'
        '<meta property="og:title" content="OG Pancakes" />'
        '<meta property="og:description" content="OG desc" />'
        "</head><body></body></html>"
    )
    mock_get.return_value = _make_mock_response(html)
    result = scraper.scrape("https://tasty.co/recipe/og-test")

    assert result.title == "OG Pancakes"
    assert result.description == "OG desc"
