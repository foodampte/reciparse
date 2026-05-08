import pytest

from reciparse.scrapers.registry import ScraperRegistry, UnsupportedSiteError
from reciparse.scrapers.minimalistbaker import MinimalistBakerScraper


@pytest.fixture
def registry():
    r = ScraperRegistry()
    r.register(MinimalistBakerScraper)
    return r


def test_get_scraper_minimalistbaker(registry):
    scraper = registry.get_scraper("https://minimalistbaker.com/easy-vegan-pancakes/")
    assert isinstance(scraper, MinimalistBakerScraper)


def test_get_scraper_minimalistbaker_no_www(registry):
    scraper = registry.get_scraper("https://www.minimalistbaker.com/easy-vegan-pancakes/")
    assert isinstance(scraper, MinimalistBakerScraper)


def test_get_scraper_minimalistbaker_https(registry):
    scraper = registry.get_scraper("http://minimalistbaker.com/some-recipe/")
    assert isinstance(scraper, MinimalistBakerScraper)


def test_get_scraper_unsupported_raises(registry):
    with pytest.raises(UnsupportedSiteError):
        registry.get_scraper("https://randomcookingblog.com/recipe/")


def test_minimalistbaker_not_in_default_registry_for_other_sites():
    """Ensure MinimalistBaker scraper does not claim other sites."""
    scraper = MinimalistBakerScraper()
    assert not scraper.supports("https://seriouseats.com/recipe")
    assert not scraper.supports("https://bonappetit.com/recipe")
    assert not scraper.supports("https://tasty.co/recipe")
