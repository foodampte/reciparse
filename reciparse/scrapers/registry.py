"""Registry for all available scrapers."""

from __future__ import annotations

from urllib.parse import urlparse
from typing import Type

from .base import BaseScraper


class UnsupportedSiteError(Exception):
    """Raised when no scraper supports the given URL."""


class ScraperRegistry:
    """Holds and resolves scraper implementations by URL."""

    def __init__(self) -> None:
        self._scrapers: list[Type[BaseScraper]] = []
        self._register_defaults()

    def _register_defaults(self) -> None:
        from .allrecipes import AllRecipesScraper
        from .foodnetwork import FoodNetworkScraper
        from .seriouseats import SeriousEatsScraper
        from .epicurious import EpicuriousScraper
        from .bonappetit import BonAppetitScraper
        from .NYTCooking import NYTCookingScraper
        from .simplyrecipes import SimplyRecipesScraper
        from .tasty import TastyScraper
        from .delish import DelishScraper
        from .thekitchn import TheKitchnScraper
        from .cookinglight import CookingLightScraper
        from .kingarthurbaking import KingArthurBakingScraper
        from .budgetbytes import BudgetBytesScraper
        from .smittenkitchen import SmittenKitchenScraper
        from .a101cookbooks import HundredAndOneCookbooksScraper

        for cls in [
            AllRecipesScraper,
            FoodNetworkScraper,
            SeriousEatsScraper,
            EpicuriousScraper,
            BonAppetitScraper,
            NYTCookingScraper,
            SimplyRecipesScraper,
            TastyScraper,
            DelishScraper,
            TheKitchnScraper,
            CookingLightScraper,
            KingArthurBakingScraper,
            BudgetBytesScraper,
            SmittenKitchenScraper,
            HundredAndOneCookbooksScraper,
        ]:
            self.register(cls)

    def register(self, scraper_cls: Type[BaseScraper]) -> None:
        """Register a scraper class."""
        if scraper_cls not in self._scrapers:
            self._scrapers.append(scraper_cls)

    def get_scraper(self, url: str) -> BaseScraper:
        """Return an instantiated scraper that supports *url*.

        Raises:
            UnsupportedSiteError: if no registered scraper handles the URL.
        """
        for cls in self._scrapers:
            if cls.supports(url):
                return cls()
        domain = urlparse(url).netloc
        raise UnsupportedSiteError(f"No scraper available for: {domain}")

    def supported_domains(self) -> list[str]:
        """Return a list of domains with registered scrapers."""
        domains = []
        for cls in self._scrapers:
            domain = getattr(cls, "DOMAIN", None)
            if domain:
                domains.append(domain)
        return domains

    def __len__(self) -> int:
        return len(self._scrapers)
