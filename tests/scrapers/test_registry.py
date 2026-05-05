"""Tests for the scraper registry."""

import pytest

from reciparse.scrapers.registry import (
    get_scraper,
    list_supported_domains,
    register_scraper,
    UnsupportedSiteError,
)
from reciparse.scrapers.allrecipes import AllRecipesScraper
from reciparse.scrapers.foodnetwork import FoodNetworkScraper
from reciparse.scrapers.base import BaseScraper, RecipeData


def test_get_scraper_allrecipes():
    scraper = get_scraper("https://www.allrecipes.com/recipe/12345/chocolate-cake")
    assert isinstance(scraper, AllRecipesScraper)


def test_get_scraper_foodnetwork():
    scraper = get_scraper("https://www.foodnetwork.com/recipes/food-network-kitchen/pancakes")
    assert isinstance(scraper, FoodNetworkScraper)


def test_get_scraper_unsupported_raises():
    with pytest.raises(UnsupportedSiteError) as exc_info:
        get_scraper("https://www.unknownsite.com/recipe/abc")
    assert "unknownsite.com" in str(exc_info.value)


def test_unsupported_site_error_stores_url():
    url = "https://www.noscraperhere.com/recipe/1"
    error = UnsupportedSiteError(url)
    assert error.url == url


def test_list_supported_domains_contains_known_sites():
    domains = list_supported_domains()
    assert "allrecipes.com" in domains
    assert "foodnetwork.com" in domains


def test_list_supported_domains_is_sorted():
    domains = list_supported_domains()
    assert domains == sorted(domains)


def test_register_scraper_adds_new_domain():
    class _CustomScraper(BaseScraper):
        DOMAIN = "customcooking.com"

        def supports(self, url: str) -> bool:
            return "customcooking.com" in url

        def scrape(self, url: str) -> RecipeData:
            return RecipeData(title="Test", source_url=url)

    register_scraper(_CustomScraper)

    domains = list_supported_domains()
    assert "customcooking.com" in domains

    scraper = get_scraper("https://www.customcooking.com/recipe/42")
    assert isinstance(scraper, _CustomScraper)


def test_register_scraper_no_duplicates():
    initial_count = len(list_supported_domains())
    register_scraper(FoodNetworkScraper)
    assert len(list_supported_domains()) == initial_count
