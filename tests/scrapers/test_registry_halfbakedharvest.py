"""Registry integration tests for HalfBakedHarvestScraper."""
from __future__ import annotations

import pytest

from reciparse.scrapers.registry import ScraperRegistry, UnsupportedSiteError
from reciparse.scrapers.halfbakedharvest import HalfBakedHarvestScraper


@pytest.fixture
def registry() -> ScraperRegistry:
    return ScraperRegistry()


def test_get_scraper_halfbakedharvest(registry):
    scraper = registry.get_scraper("https://www.halfbakedharvest.com/lemon-pasta/")
    assert isinstance(scraper, HalfBakedHarvestScraper)


def test_get_scraper_halfbakedharvest_no_www(registry):
    scraper = registry.get_scraper("https://halfbakedharvest.com/lemon-pasta/")
    assert isinstance(scraper, HalfBakedHarvestScraper)


def test_get_scraper_halfbakedharvest_https(registry):
    scraper = registry.get_scraper("https://halfbakedharvest.com/some-recipe/")
    assert isinstance(scraper, HalfBakedHarvestScraper)


def test_get_scraper_unsupported_raises(registry):
    with pytest.raises(UnsupportedSiteError):
        registry.get_scraper("https://www.unknownsite.com/recipe/")


def test_halfbakedharvest_scraper_supports_method():
    assert HalfBakedHarvestScraper.supports(
        "https://www.halfbakedharvest.com/creamy-tomato-soup/"
    )
    assert not HalfBakedHarvestScraper.supports(
        "https://www.foodnetwork.com/recipes/pasta"
    )
