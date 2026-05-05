from urllib.parse import urlparse
from typing import Type

from reciparse.scrapers.base import BaseScraper


class UnsupportedSiteError(Exception):
    """Raised when no scraper is registered for the given URL."""

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"No scraper available for URL: {url}")


class ScraperRegistry:
    """Registry that maps domains to scraper classes."""

    def __init__(self) -> None:
        self._scrapers: list[Type[BaseScraper]] = []
        self._register_defaults()

    def _register_defaults(self) -> None:
        from reciparse.scrapers.allrecipes import AllRecipesScraper
        from reciparse.scrapers.foodnetwork import FoodNetworkScraper
        from reciparse.scrapers.seriouseats import SeriousEatsScraper

        self._scrapers.extend([AllRecipesScraper, FoodNetworkScraper, SeriousEatsScraper])

    def register_scraper(self, scraper_cls: Type[BaseScraper]) -> None:
        """Register a new scraper class."""
        if scraper_cls not in self._scrapers:
            self._scrapers.append(scraper_cls)

    def get_scraper(self, url: str) -> BaseScraper:
        """Return an instantiated scraper that supports the given URL."""
        for scraper_cls in self._scrapers:
            instance = scraper_cls()
            if instance.supports(url):
                return instance
        raise UnsupportedSiteError(url)

    def list_supported_domains(self) -> list[str]:
        """Return a list of domains supported by registered scrapers."""
        domains = []
        for scraper_cls in self._scrapers:
            domain = getattr(scraper_cls, "DOMAIN", None)
            if domain:
                domains.append(domain)
        return domains


# Module-level default registry instance
registry = ScraperRegistry()
