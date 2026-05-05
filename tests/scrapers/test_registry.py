"""Tests for ScraperRegistry — extended to cover Epicurious."""

from __future__ import annotations

import pytest

from reciparse.scrapers.allrecipes import AllRecipesScraper
from reciparse.scrapers.epicurious import EpicuriousScraper
from reciparse.scrapers.foodnetwork import FoodNetworkScraper
from reciparse.scrapers.registry import ScraperRegistry, UnsupportedSiteError
from reciparse.scrapers.seriouseats import SeriousEatsScraper


@pytest.fixture()
def registry() -> ScraperRegistry:
    return ScraperRegistry()


def test_get_scraper_allrecipes(registry):
    scraper = registry.get_scraper("https://www.allrecipes.com/recipe/12345/")
    assert isinstance(scraper, AllRecipesScraper)


def test_get_scraper_foodnetwork(registry):
    scraper = registry.get_scraper("https://www.foodnetwork.com/recipes/pasta")
    assert isinstance(scraper, FoodNetworkScraper)


def test_get_scraper_seriouseats(registry):
    scraper = registry.get_scraper("https://www.seriouseats.com/recipes/2023/pasta")
    assert isinstance(scraper, SeriousEatsScraper)


def test_get_scraper_epicurious(registry):
    scraper = registry.get_scraper("https://www.epicurious.com/recipes/food/views/pasta")
    assert isinstance(scraper, EpicuriousScraper)


def test_get_scraper_epicurious_no_www(registry):
    scraper = registry.get_scraper("https://epicurious.com/recipes/food/views/pasta")
    assert isinstance(scraper, EpicuriousScraper)


def test_get_scraper_unsupported_raises(registry):
    with pytest.raises(UnsupportedSiteError):
        registry.get_scraper("https://www.unknown-cooking-site.com/recipe/1")


def test_register_custom_scraper(registry):
    class MyScraper:
        @classmethod
        def supports(cls, url):
            return "mysite.com" in url

    registry.register(MyScraper)
    scraper = registry.get_scraper("https://mysite.com/recipe/1")
    assert isinstance(scraper, MyScraper)


def test_list_supported_domains_includes_epicurious(registry):
    domains = registry.supported_domains()
    assert any("epicurious" in d for d in domains)


def test_list_supported_domains_returns_all_defaults(registry):
    domains = registry.supported_domains()
    assert len(domains) >= 4
