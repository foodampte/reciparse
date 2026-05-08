"""Registry integration tests for the Cookie and Kate scraper."""
import pytest

from reciparse.scrapers.registry import ScraperRegistry, UnsupportedSiteError
from reciparse.scrapers.cookieandkate import CookieAndKateScraper


@pytest.fixture
def registry():
    return ScraperRegistry()


def test_get_scraper_cookieandkate(registry):
    scraper = registry.get_scraper("https://cookieandkate.com/honey-whole-wheat-bread/")
    assert isinstance(scraper, CookieAndKateScraper)


def test_get_scraper_cookieandkate_no_www(registry):
    scraper = registry.get_scraper("https://www.cookieandkate.com/some-recipe/")
    assert isinstance(scraper, CookieAndKateScraper)


def test_get_scraper_cookieandkate_https(registry):
    scraper = registry.get_scraper("http://cookieandkate.com/recipe/")
    assert isinstance(scraper, CookieAndKateScraper)


def test_get_scraper_unsupported_raises(registry):
    with pytest.raises(UnsupportedSiteError):
        registry.get_scraper("https://unknownsite.example.com/recipe/")


def test_cookieandkate_supports_method_directly():
    assert CookieAndKateScraper.supports("https://cookieandkate.com/recipe/")
    assert not CookieAndKateScraper.supports("https://seriouseats.com/recipe/")
