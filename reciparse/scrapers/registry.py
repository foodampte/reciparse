from urllib.parse import urlparse

from .allrecipes import AllRecipesScraper
from .bonappetit import BonAppetitScraper
from .budgetbytes import BudgetBytesScraper
from .cookinglight import CookingLightScraper
from .delish import DelishScraper
from .epicurious import EpicuriousScraper
from .foodnetwork import FoodNetworkScraper
from .kingarthurbaking import KingArthurBakingScraper
from .NYTCooking import NYTCookingScraper
from .seriouseats import SeriousEatsScraper
from .simplyrecipes import SimplyRecipesScraper
from .tasty import TastyScraper
from .thekitchn import TheKitchnScraper
from .base import BaseScraper


class UnsupportedSiteError(Exception):
    """Raised when no scraper supports the given URL."""


class ScraperRegistry:
    """Registry that maps URLs to the appropriate scraper."""

    def __init__(self) -> None:
        self._scrapers: list[type[BaseScraper]] = []
        self._register_defaults()

    def _register_defaults(self) -> None:
        default_scrapers = [
            AllRecipesScraper,
            BonAppetitScraper,
            BudgetBytesScraper,
            CookingLightScraper,
            DelishScraper,
            EpicuriousScraper,
            FoodNetworkScraper,
            KingArthurBakingScraper,
            NYTCookingScraper,
            SeriousEatsScraper,
            SimplyRecipesScraper,
            TastyScraper,
            TheKitchnScraper,
        ]
        for scraper_cls in default_scrapers:
            self.register(scraper_cls)

    def register(self, scraper_cls: type[BaseScraper]) -> None:
        """Register a scraper class."""
        if scraper_cls not in self._scrapers:
            self._scrapers.append(scraper_cls)

    def get_scraper(self, url: str) -> BaseScraper:
        """Return an instantiated scraper that supports *url*.

        Raises:
            UnsupportedSiteError: if no registered scraper supports the URL.
        """
        for scraper_cls in self._scrapers:
            if scraper_cls.supports(url):
                return scraper_cls()
        hostname = urlparse(url).hostname or url
        raise UnsupportedSiteError(f"No scraper available for: {hostname}")

    @property
    def supported_domains(self) -> list[str]:
        """Return a sorted list of supported domain strings."""
        domains = []
        for scraper_cls in self._scrapers:
            domain = getattr(scraper_cls, "DOMAIN", None)
            if domain:
                domains.append(domain)
        return sorted(domains)
