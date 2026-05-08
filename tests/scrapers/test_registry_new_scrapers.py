import pytest
from reciparse.scrapers.registry import ScraperRegistry, UnsupportedSiteError
from reciparse.scrapers.thepioneerwoman import ThePioneerWomanScraper
from reciparse.scrapers.loveandlemons import LoveAndLemonsScraper


@pytest.fixture
def registry():
    return ScraperRegistry()


def test_get_scraper_thepioneerwoman(registry):
    scraper = registry.get_scraper("https://www.thepioneerwoman.com/food-cooking/recipes/a123/skillet/")
    assert isinstance(scraper, ThePioneerWomanScraper)


def test_get_scraper_thepioneerwoman_no_www(registry):
    scraper = registry.get_scraper("https://thepioneerwoman.com/food-cooking/recipes/a123/skillet/")
    assert isinstance(scraper, ThePioneerWomanScraper)


def test_get_scraper_loveandlemons(registry):
    scraper = registry.get_scraper("https://www.loveandlemons.com/lemon-pasta/")
    assert isinstance(scraper, LoveAndLemonsScraper)


def test_get_scraper_loveandlemons_no_www(registry):
    scraper = registry.get_scraper("https://loveandlemons.com/lemon-pasta/")
    assert isinstance(scraper, LoveAndLemonsScraper)


def test_thepioneerwoman_not_matched_by_loveandlemons(registry):
    scraper = registry.get_scraper("https://www.thepioneerwoman.com/food-cooking/recipes/a123/skillet/")
    assert not isinstance(scraper, LoveAndLemonsScraper)


def test_loveandlemons_not_matched_by_thepioneerwoman(registry):
    scraper = registry.get_scraper("https://www.loveandlemons.com/lemon-pasta/")
    assert not isinstance(scraper, ThePioneerWomanScraper)


def test_unsupported_site_raises(registry):
    with pytest.raises(UnsupportedSiteError):
        registry.get_scraper("https://www.unknownsite.com/recipe/")


def test_registry_lists_thepioneerwoman(registry):
    domains = registry.list_supported_domains()
    assert "thepioneerwoman.com" in domains


def test_registry_lists_loveandlemons(registry):
    domains = registry.list_supported_domains()
    assert "loveandlemons.com" in domains
