import pytest
from unittest.mock import MagicMock, patch

from reciparse.scrapers.seriouseats import SeriousEatsScraper
from reciparse.scrapers.base import RecipeData


SAMPLE_HTML = """
<html><body>
  <h1 class="heading__title">Perfect Scrambled Eggs</h1>
  <div class="section--summary"><p>Creamy and soft scrambled eggs.</p></div>
  <ul>
    <li class="ingredient">4 large eggs</li>
    <li class="ingredient">1 tbsp butter</li>
    <li class="ingredient">Salt to taste</li>
  </ul>
  <ol>
    <li class="mntl-sc-block-html">Crack eggs into a bowl.</li>
    <li class="mntl-sc-block-html">Cook on low heat.</li>
  </ol>
  <div class="project-meta__time-container">
    <span class="meta-text__label">Prep Time:</span>
    <span class="meta-text__data">5 mins</span>
  </div>
  <div class="project-meta__time-container">
    <span class="meta-text__label">Cook Time:</span>
    <span class="meta-text__data">10 mins</span>
  </div>
  <div class="project-meta__time-container">
    <span class="meta-text__label">Servings:</span>
    <span class="meta-text__data">2</span>
  </div>
</body></html>
"""


@pytest.fixture
def scraper():
    return SeriousEatsScraper()


def test_supports_seriouseats_url(scraper):
    assert scraper.supports("https://www.seriouseats.com/scrambled-eggs") is True


def test_supports_seriouseats_no_www(scraper):
    assert scraper.supports("https://seriouseats.com/scrambled-eggs") is True


def test_does_not_support_other_url(scraper):
    assert scraper.supports("https://www.allrecipes.com/recipe/12345") is False


def _make_mock_response(html: str) -> MagicMock:
    mock_resp = MagicMock()
    mock_resp.text = html
    return mock_resp


@patch.object(SeriousEatsScraper, "_fetch")
def test_scrape_returns_recipe_data(mock_fetch, scraper):
    mock_fetch.return_value = _make_mock_response(SAMPLE_HTML)
    url = "https://www.seriouseats.com/scrambled-eggs"
    result = scraper.scrape(url)

    assert isinstance(result, RecipeData)
    assert result.title == "Perfect Scrambled Eggs"
    assert result.description == "Creamy and soft scrambled eggs."
    assert len(result.ingredients) == 3
    assert "4 large eggs" in result.ingredients
    assert len(result.instructions) == 2
    assert result.prep_time == "5 mins"
    assert result.cook_time == "10 mins"
    assert result.servings == "2"
    assert result.source_url == url


@patch.object(SeriousEatsScraper, "_fetch")
def test_scrape_handles_missing_fields(mock_fetch, scraper):
    mock_fetch.return_value = _make_mock_response("<html><body></body></html>")
    result = scraper.scrape("https://www.seriouseats.com/empty")

    assert result.title == ""
    assert result.description == ""
    assert result.ingredients == []
    assert result.instructions == []
    assert result.prep_time == ""
    assert result.cook_time == ""
    assert result.servings == ""
