import pytest

from reciparse.scrapers.registry import ScraperRegistry, UnsupportedSiteError
from reciparse.scrapers.allrecipes import AllRecipesScraper
from reciparse.scrapers.foodnetwork import FoodNetworkScraper
from reciparse.scrapers.seriouseats import SeriousEatsScraper


@pytest.fixture
def registry():
    return ScraperRegistry()


def test_get_scraper_allrecipes(registry):
    scraper = registry.get_scraper("https://www.allrecipes.com/recipe/12345/pasta/")
    assert isinstance(scraper, AllRecipesScraper)


def test_get_scraper_foodnetwork(registry):
    scraper = registry.get_scraper("https://www.foodnetwork.com/recipes/pasta")
    assert isinstance(scraper, FoodNetworkScraper)


def test_get_scraper_seriouseats(registry):
    scraper = registry.get_scraper("https://www.seriouseats.com/scrambled-eggs")
    assert isinstance(scraper, SeriousEatsScraper)


def test_get_scraper_unsupported_raises(registry):
    with pytest.raises(UnsupportedSiteError):
        registry.get_scraper("https://www.unknown-cooking-site.com/recipe")


def test_unsupported_site_error_stores_url(registry):
    url = "https://www.notasupported.com/recipe"
    with pytest.raises(UnsupportedSiteError) as exc_info:
        registry.get_scraper(url)
    assert exc_info.value.url == url


def test_list_supported_domains_contains_known_sites(registry):
    domains = registry.list_supported_domains()
    assert "www.allrecipes.com" in domains
    assert "www.foodnetwork.com" in domains
    assert "www.seriouseats.com" in domains


def test_register_scraper_adds_new_scraper(registry):
    from reciparse.scrapers.base import BaseScraper, RecipeData

    class MockScraper(BaseScraper):
        DOMAIN = "www.mockrecipes.com"

        def supports(self, url: str) -> bool:
            return "mockrecipes.com" in url

        def scrape(self, url: str) -> RecipeData:
            return RecipeData(source_url=url)

    initial_count = len(registry._scrapers)
    registry.register_scraper(MockScraper)
    assert len(registry._scrapers) == initial_count + 1
    scraper = registry.get_scraper("https://www.mockrecipes.com/recipe/1")
    assert isinstance(scraper, MockScraper)


def test_register_scraper_no_duplicates(registry):
    initial_count = len(registry._scrapers)
    registry.register_scraper(AllRecipesScraper)
    assert len(registry._scrapers) == initial_count


def test_list_supported_domains_returns_list(registry):
    domains = registry.list_supported_domains()
    assert isinstance(domains, list)
    assert len(domains) >= 3
