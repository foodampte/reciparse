from typing import Dict, List, Optional, Type

from reciparse.scrapers.base import BaseScraper


class UnsupportedSiteError(Exception):
    """Raised when no scraper is found for a given URL."""

    def __init__(self, url: str) -> None:
        super().__init__(f"No scraper available for URL: {url}")
        self.url = url


class ScraperRegistry:
    """Registry that maps URLs to the appropriate scraper."""

    def __init__(self) -> None:
        self._scrapers: List[Type[BaseScraper]] = []
        self._register_defaults()

    def _register_defaults(self) -> None:
        from reciparse.scrapers.allrecipes import AllRecipesScraper
        from reciparse.scrapers.foodnetwork import FoodNetworkScraper
        from reciparse.scrapers.seriouseats import SeriousEatsScraper
        from reciparse.scrapers.epicurious import EpicuriousScraper
        from reciparse.scrapers.bonappetit import BonAppetitScraper

        for cls in [
            AllRecipesScraper,
            FoodNetworkScraper,
            SeriousEatsScraper,
            EpicuriousScraper,
            BonAppetitScraper,
        ]:
            self.register(cls)

    def register(self, scraper_cls: Type[BaseScraper]) -> None:
        """Register a scraper class."""
        if scraper_cls not in self._scrapers:
            self._scrapers.append(scraper_cls)

    def get_scraper(self, url: str) -> BaseScraper:
        """Return an instantiated scraper that supports the given URL."""
        for cls in self._scrapers:
            if cls.supports(url):
                return cls()
        raise UnsupportedSiteError(url)

    def supported_domains(self) -> List[str]:
        """Return a list of supported domain strings."""
        domains = []
        for cls in self._scrapers:
            domain = getattr(cls, "DOMAIN", None)
            if domain:
                domains.append(domain)
        return domains
