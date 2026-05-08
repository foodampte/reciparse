import pytest

from reciparse.scrapers.registry import ScraperRegistry, UnsupportedSiteError
from reciparse.scrapers.skinnytaste import SkinnyTasteScraper


@pytest.fixture
def registry():
    return ScraperRegistry()


def test_get_scraper_skinnytaste(registry):
    scraper = registry.get_scraper("https://www.skinnytaste.com/chicken-soup/")
    assert isinstance(scraper, SkinnyTasteScraper)


def test_get_scraper_skinnytaste_no_www(registry):
    scraper = registry.get_scraper("https://skinnytaste.com/chicken-soup/")
    assert isinstance(scraper, SkinnyTasteScraper)


def test_get_scraper_skinnytaste_https(registry):
    scraper = registry.get_scraper("https://www.skinnytaste.com/pasta-fagioli/")
    assert isinstance(scraper, SkinnyTasteScraper)


def test_get_scraper_unsupported_raises(registry):
    with pytest.raises(UnsupportedSiteError):
        registry.get_scraper("https://www.notarecipesite.xyz/recipe/1")


def test_skinnytaste_scraper_registered_once(registry):
    scrapers = [
        type(registry.get_scraper("https://www.skinnytaste.com/test/"))
    ]
    assert scrapers.count(SkinnyTasteScraper) == 1
