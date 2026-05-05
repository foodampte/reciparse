import pytest
from unittest.mock import MagicMock, patch

from reciparse.scrapers.NYTCooking import NYTCookingScraper
from reciparse.scrapers.base import RecipeData


NYT_URL = "https://cooking.nytimes.com/recipes/1234-chocolate-cake"
OTHER_URL = "https://www.allrecipes.com/recipe/1234"


@pytest.fixture
def scraper():
    return NYTCookingScraper()


# ── supports() ────────────────────────────────────────────────────────────────

def test_supports_nytcooking_url(scraper):
    assert scraper.supports(NYT_URL) is True


def test_supports_nytcooking_no_www(scraper):
    assert scraper.supports("https://cooking.nytimes.com/recipes/5678-pasta") is True


def test_does_not_support_other_url(scraper):
    assert scraper.supports(OTHER_URL) is False


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_mock_response(html: str) -> MagicMock:
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


FULL_HTML = """
<html><head>
  <meta property="og:title" content="NYT Chocolate Cake" />
  <meta name="description" content="A rich cake." />
</head><body>
  <h1 class="pantry--title-display recipe-title">Chocolate Cake</h1>
  <div class="recipe-introduction">A wonderfully rich chocolate cake.</div>
  <ul>
    <li class="ingredient">2 cups flour</li>
    <li class="ingredient">1 cup sugar</li>
  </ul>
  <ol>
    <li class="preparation-step">Preheat oven to 350F.</li>
    <li class="preparation-step">Mix dry ingredients.</li>
  </ol>
  <dl>
    <dt>Prep Time</dt><dd>20 minutes</dd>
    <dt>Cook Time</dt><dd>40 minutes</dd>
  </dl>
  <span class="yield">8 servings</span>
</body></html>
"""

EMPTY_HTML = "<html><body></body></html>"


# ── scrape() ──────────────────────────────────────────────────────────────────

def test_scrape_returns_recipe_data(scraper):
    with patch.object(scraper._session, "get", return_value=_make_mock_response(FULL_HTML)):
        result = scraper.scrape(NYT_URL)

    assert isinstance(result, RecipeData)
    assert result.title == "Chocolate Cake"
    assert result.description == "A wonderfully rich chocolate cake."
    assert result.ingredients == ["2 cups flour", "1 cup sugar"]
    assert result.instructions == ["Preheat oven to 350F.", "Mix dry ingredients."]
    assert result.prep_time == "20 minutes"
    assert result.cook_time == "40 minutes"
    assert result.servings == "8 servings"
    assert result.url == NYT_URL


def test_scrape_handles_missing_fields(scraper):
    with patch.object(scraper._session, "get", return_value=_make_mock_response(EMPTY_HTML)):
        result = scraper.scrape(NYT_URL)

    assert isinstance(result, RecipeData)
    assert result.title == ""
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time == ""
    assert result.servings == ""
