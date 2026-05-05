"""Registry for mapping URLs to their appropriate scraper implementations."""

from typing import Type

from .base import BaseScraper
from .allrecipes import AllRecipesScraper
from .foodnetwork import FoodNetworkScraper


class UnsupportedSiteError(Exception):
    """Raised when no scraper is available for the given URL."""

    def __init__(self, url: str) -> None:
        super().__init__(f"No scraper available for URL: {url}")
        self.url = url


_SCRAPERS: list[Type[BaseScraper]] = [
    AllRecipesScraper,
    FoodNetworkScraper,
]


def get_scraper(url: str) -> BaseScraper:
    """Return an instantiated scraper that supports the given URL.

    Raises:
        UnsupportedSiteError: If no registered scraper supports the URL.
    """
    for scraper_cls in _SCRAPERS:
        instance = scraper_cls()
        if instance.supports(url):
            return instance
    raise UnsupportedSiteError(url)


def list_supported_domains() -> list[str]:
    """Return a sorted list of domains supported by registered scrapers."""
    domains = []
    for scraper_cls in _SCRAPERS:
        domain = getattr(scraper_cls, "DOMAIN", None)
        if domain:
            domains.append(domain)
    return sorted(domains)


def register_scraper(scraper_cls: Type[BaseScraper]) -> None:
    """Register a custom scraper class at runtime."""
    if scraper_cls not in _SCRAPERS:
        _SCRAPERS.append(scraper_cls)
