import pytest
from unittest.mock import MagicMock, patch

from reciparse.scrapers.simplyrecipes import SimplyRecipesScraper
from reciparse.scrapers.base import RecipeData


@pytest.fixture
def scraper():
    return SimplyRecipesScraper()


# --- supports() ---

def test_supports_simplyrecipes_url(scraper):
    assert scraper.supports("https://www.simplyrecipes.com/recipes/homemade-pasta/") is True


def test_supports_simplyrecipes_no_www(scraper):
    assert scraper.supports("https://simplyrecipes.com/recipes/homemade-pasta/") is True


def test_does_not_support_other_url(scraper):
    assert scraper.supports("https://allrecipes.com/recipe/12345/") is False


# --- scrape() helpers ---

def _make_mock_response(html: str) -> MagicMock:
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


_SAMPLE_HTML = """
<html><body>
  <h1 class="heading__title">Homemade Pasta</h1>
  <div class="article-subheading">A simple pasta recipe.</div>
  <ul class="structured-ingredients__list">
    <li>2 cups all-purpose flour</li>
    <li>3 large eggs</li>
  </ul>
  <ol class="instructions-section">
    <li>Mix flour and eggs.</li>
    <li>Knead for 10 minutes.</li>
  </ol>
  <span data-testid="prep-time">20 mins</span>
  <span data-testid="cook-time">5 mins</span>
  <span data-testid="serving-size">4 servings</span>
</body></html>
"""


@pytest.fixture
def mock_scrape(scraper):
    with patch("reciparse.scrapers.simplyrecipes.requests.get") as mock_get:
        mock_get.return_value = _make_mock_response(_SAMPLE_HTML)
        yield scraper.scrape("https://www.simplyrecipes.com/recipes/homemade-pasta/")


def test_scrape_returns_recipe_data(mock_scrape):
    assert isinstance(mock_scrape, RecipeData)


def test_scrape_title(mock_scrape):
    assert mock_scrape.title == "Homemade Pasta"


def test_scrape_description(mock_scrape):
    assert "simple pasta" in mock_scrape.description


def test_scrape_ingredients(mock_scrape):
    assert len(mock_scrape.ingredients) == 2
    assert "flour" in mock_scrape.ingredients[0]


def test_scrape_instructions(mock_scrape):
    assert len(mock_scrape.instructions) == 2
    assert "Knead" in mock_scrape.instructions[1]


def test_scrape_times(mock_scrape):
    assert mock_scrape.prep_time == "20 mins"
    assert mock_scrape.cook_time == "5 mins"


def test_scrape_servings(mock_scrape):
    assert mock_scrape.servings == "4 servings"


def test_scrape_handles_missing_fields(scraper):
    sparse_html = "<html><body><h1>Minimal</h1></body></html>"
    with patch("reciparse.scrapers.simplyrecipes.requests.get") as mock_get:
        mock_get.return_value = _make_mock_response(sparse_html)
        result = scraper.scrape("https://www.simplyrecipes.com/recipes/minimal/")
    assert result.title == "Minimal"
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time == ""
