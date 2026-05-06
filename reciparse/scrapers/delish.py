"""Scraper for Delish.com recipes."""

from __future__ import annotations

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class DelishScraper(BaseScraper):
    """Scraper for https://www.delish.com recipes."""

    _DOMAIN = "delish.com"

    @classmethod
    def supports(cls, url: str) -> bool:
        """Return True if the URL belongs to delish.com."""
        host = urlparse(url).netloc.lower().lstrip("www.")
        return host == cls._DOMAIN

    def scrape(self, url: str) -> RecipeData:
        """Fetch *url* and return a normalised :class:`RecipeData`."""
        response = requests.get(url, timeout=10, headers={"User-Agent": "reciparse/1.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        return RecipeData(
            title=self._parse_title(soup),
            description=self._parse_description(soup),
            ingredients=self._parse_ingredients(soup),
            instructions=self._parse_instructions(soup),
            prep_time=self._parse_time(soup, "prep"),
            cook_time=self._parse_time(soup, "cook"),
            servings=self._parse_servings(soup),
            source_url=url,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("h1", class_=lambda c: c and "recipe-title" in c)
        if tag is None:
            tag = soup.find("h1")
        return tag.get_text(strip=True) if tag else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find("div", class_=lambda c: c and "recipe-intro" in c)
        if tag is None:
            tag = soup.find("meta", attrs={"name": "description"})
            return tag.get("content", "") if tag else ""
        return tag.get_text(strip=True)

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        container = soup.find("ul", class_=lambda c: c and "ingredient" in c)
        if container is None:
            return []
        return [
            li.get_text(strip=True)
            for li in container.find_all("li")
            if li.get_text(strip=True)
        ]

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        container = soup.find("ol", class_=lambda c: c and "direction" in c)
        if container is None:
            return []
        return [
            li.get_text(strip=True)
            for li in container.find_all("li")
            if li.get_text(strip=True)
        ]

    def _parse_time(self, soup: BeautifulSoup, kind: str) -> str:
        tag = soup.find(attrs={"data-time-type": kind})
        return tag.get_text(strip=True) if tag else ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        tag = soup.find(class_=lambda c: c and "servings" in c)
        return tag.get_text(strip=True) if tag else ""
