"""Tests for the FoodNetwork scraper."""

from unittest.mock import MagicMock, patch

import pytest

from reciparse.scrapers.foodnetwork import FoodNetworkScraper
from reciparse.scrapers.base import RecipeData


FOODNETWORK_URL = "https://www.foodnetwork.com/recipes/food-network-kitchen/pancakes-recipe-1913844"

SAMPLE_HTML = """
<html><body>
  <span class="o-AssetTitle__a-HeadlineText">Fluffy Pancakes</span>
  <div class="o-AssetDescription__a-Description">Light and fluffy every time.</div>
  <ul>
    <li><span class="o-Ingredients__a-Ingredient--CheckboxLabel">1 cup flour</span></li>
    <li><span class="o-Ingredients__a-Ingredient--CheckboxLabel">2 eggs</span></li>
    <li><span class="o-Ingredients__a-Ingredient--CheckboxLabel">1 cup milk</span></li>
  </ul>
  <ul>
    <li class="o-Method__m-Step">Mix dry ingredients.</li>
    <li class="o-Method__m-Step">Add wet ingredients and stir.</li>
    <li class="o-Method__m-Step">Cook on griddle until golden.</li>
  </ul>
  <ul>
    <li class="o-RecipeInfo__Item">
      <span class="o-RecipeInfo__a-Headline">Prep</span>
      <span class="o-RecipeInfo__a-Description">10 min</span>
    </li>
    <li class="o-RecipeInfo__Item">
      <span class="o-RecipeInfo__a-Headline">Cook</span>
      <span class="o-RecipeInfo__a-Description">20 min</span>
    </li>
    <li class="o-RecipeInfo__Item">
      <span class="o-RecipeInfo__a-Headline">Yield</span>
      <span class="o-RecipeInfo__a-Description">4 servings</span>
    </li>
  </ul>
</body></html>
"""


@pytest.fixture
def scraper():
    return FoodNetworkScraper()


def test_supports_foodnetwork_url(scraper):
    assert scraper.supports(FOODNETWORK_URL) is True


def test_does_not_support_other_url(scraper):
    assert scraper.supports("https://www.allrecipes.com/recipe/12345") is False


@patch("reciparse.scrapers.foodnetwork.requests.get")
def test_scrape_returns_recipe_data(mock_get, scraper):
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = scraper.scrape(FOODNETWORK_URL)

    assert isinstance(result, RecipeData)
    assert result.title == "Fluffy Pancakes"
    assert result.description == "Light and fluffy every time."
    assert result.ingredients == ["1 cup flour", "2 eggs", "1 cup milk"]
    assert result.instructions == [
        "Mix dry ingredients.",
        "Add wet ingredients and stir.",
        "Cook on griddle until golden.",
    ]
    assert result.prep_time == "10 min"
    assert result.cook_time == "20 min"
    assert result.servings == "4 servings"
    assert result.source_url == FOODNETWORK_URL


@patch("reciparse.scrapers.foodnetwork.requests.get")
def test_scrape_handles_missing_fields(mock_get, scraper):
    mock_response = MagicMock()
    mock_response.text = "<html><body></body></html>"
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = scraper.scrape(FOODNETWORK_URL)

    assert result.title == ""
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time is None
    assert result.cook_time is None
    assert result.servings is None
