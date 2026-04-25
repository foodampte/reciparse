"""Scraper registry — maps URLs to the correct scraper class."""

from typing import List, Type

from reciparse.scrapers.base import BaseScraper
from reciparse.scrapers.allrecipes import AllRecipesScraper

# Register all available scrapers here
_SCRAPERS: List[Type[BaseScraper]] = [
    AllRecipesScraper,
]


class UnsupportedSiteError(Exception):
    """Raised when no scraper supports the given URL."""


def get_scraper(url: str) -> BaseScraper:
    """
    Return an instantiated scraper for the given URL.

    Raises:
        UnsupportedSiteError: If no registered scraper supports the URL.
    """
    for scraper_cls in _SCRAPERS:
        if scraper_cls.supports(url):
            return scraper_cls(url)
    supported = ", ".join(
        domain
        for cls in _SCRAPERS
        for domain in cls.SUPPORTED_DOMAINS
    )
    raise UnsupportedSiteError(
        f"No scraper available for: {url}\n"
        f"Supported sites: {supported}"
    )


def list_supported_domains() -> List[str]:
    """Return a sorted list of all supported domains."""
    return sorted(
        domain
        for cls in _SCRAPERS
        for domain in cls.SUPPORTED_DOMAINS
    )
