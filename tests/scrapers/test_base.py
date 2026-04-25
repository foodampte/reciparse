"""Tests for the base scraper and RecipeData dataclass."""

import pytest

from reciparse.scrapers.base import BaseScraper, RecipeData
from reciparse.scrapers.registry import get_scraper, list_supported_domains, UnsupportedSiteError


# ---------------------------------------------------------------------------
# RecipeData tests
# ---------------------------------------------------------------------------

def test_recipe_data_defaults():
    recipe = RecipeData(title="Pasta", url="https://example.com/pasta")
    assert recipe.ingredients == []
    assert recipe.instructions == []
    assert recipe.tags == []
    assert recipe.source is None


def test_recipe_data_to_dict_keys():
    recipe = RecipeData(
        title="Pasta",
        url="https://example.com/pasta",
        ingredients=["200g pasta", "salt"],
        instructions=["Boil water.", "Cook pasta."],
        prep_time="5 mins",
        cook_time="10 mins",
        total_time="15 mins",
        servings="2",
        source="example.com",
    )
    d = recipe.to_dict()
    expected_keys = {
        "title", "url", "description", "ingredients", "instructions",
        "prep_time", "cook_time", "total_time", "servings",
        "image_url", "tags", "source",
    }
    assert set(d.keys()) == expected_keys
    assert d["title"] == "Pasta"
    assert d["ingredients"] == ["200g pasta", "salt"]


# ---------------------------------------------------------------------------
# BaseScraper tests
# ---------------------------------------------------------------------------

class _DummyScraper(BaseScraper):
    SUPPORTED_DOMAINS = ["dummy.com"]

    def scrape(self) -> RecipeData:
        return RecipeData(title="Dummy", url=self.url)


def test_base_scraper_supports_matching_domain():
    assert _DummyScraper.supports("https://www.dummy.com/recipe/1") is True


def test_base_scraper_supports_non_matching_domain():
    assert _DummyScraper.supports("https://other.com/recipe/1") is False


def test_base_scraper_clean_text():
    scraper = _DummyScraper("https://dummy.com")
    assert scraper._clean_text("  hello   world  ") == "hello world"


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------

def test_get_scraper_returns_correct_type():
    from reciparse.scrapers.allrecipes import AllRecipesScraper
    scraper = get_scraper("https://www.allrecipes.com/recipe/12345/spaghetti/")
    assert isinstance(scraper, AllRecipesScraper)


def test_get_scraper_raises_for_unsupported_url():
    with pytest.raises(UnsupportedSiteError):
        get_scraper("https://www.unknownsite.com/recipe/xyz")


def test_list_supported_domains_contains_allrecipes():
    domains = list_supported_domains()
    assert "allrecipes.com" in domains
