import pytest

from reciparse.scrapers.registry import ScraperRegistry, UnsupportedSiteError
from reciparse.scrapers.allrecipes import AllRecipesScraper
from reciparse.scrapers.foodnetwork import FoodNetworkScraper
from reciparse.scrapers.seriouseats import SeriousEatsScraper
from reciparse.scrapers.epicurious import EpicuriousScraper
from reciparse.scrapers.bonappetit import BonAppetitScraper


@pytest.fixture
def registry():
    return ScraperRegistry()


def test_get_scraper_allrecipes(registry):
    scraper = registry.get_scraper("https://www.allrecipes.com/recipe/12345/chicken-soup")
    assert isinstance(scraper, AllRecipesScraper)


def test_get_scraper_foodnetwork(registry):
    scraper = registry.get_scraper("https://www.foodnetwork.com/recipes/pasta")
    assert isinstance(scraper, FoodNetworkScraper)


def test_get_scraper_seriouseats(registry):
    scraper = registry.get_scraper("https://www.seriouseats.com/best-pizza-dough")
    assert isinstance(scraper, SeriousEatsScraper)


def test_get_scraper_epicurious(registry):
    scraper = registry.get_scraper("https://www.epicurious.com/recipes/food/views/pasta")
    assert isinstance(scraper, EpicuriousScraper)


def test_get_scraper_bonappetit(registry):
    scraper = registry.get_scraper("https://www.bonappetit.com/recipe/pasta-primavera")
    assert isinstance(scraper, BonAppetitScraper)


def test_get_scraper_raises_for_unknown_url(registry):
    with pytest.raises(UnsupportedSiteError) as exc_info:
        registry.get_scraper("https://www.unknownsite.com/recipe/something")
    assert "unknownsite.com" in str(exc_info.value)


def test_unsupported_site_error_stores_url():
    url = "https://example.com/recipe"
    err = UnsupportedSiteError(url)
    assert err.url == url


def test_register_custom_scraper(registry):
    from reciparse.scrapers.base import BaseScraper, RecipeData

    class MyScraper(BaseScraper):
        DOMAIN = "mysite.com"

        @classmethod
        def supports(cls, url: str) -> bool:
            return "mysite.com" in url

        def scrape(self, url: str) -> RecipeData:
            return RecipeData(source_url=url)

    registry.register(MyScraper)
    scraper = registry.get_scraper("https://mysite.com/recipe/1")
    assert isinstance(scraper, MyScraper)


def test_register_same_scraper_twice_does_not_duplicate(registry):
    initial_count = len(registry._scrapers)
    registry.register(BonAppetitScraper)
    assert len(registry._scrapers) == initial_count


def test_supported_domains_includes_bonappetit(registry):
    domains = registry.supported_domains()
    assert "bonappetit.com" in domains


def test_supported_domains_returns_list(registry):
    domains = registry.supported_domains()
    assert isinstance(domains, list)
    assert len(domains) >= 5
