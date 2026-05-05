"""Scraper for Epicurious (epicurious.com)."""

from __future__ import annotations

import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

from reciparse.scrapers.base import BaseScraper, RecipeData


class EpicuriousScraper(BaseScraper):
    """Scraper implementation for epicurious.com."""

    _DOMAIN = "epicurious.com"

    @classmethod
    def supports(cls, url: str) -> bool:
        """Return True if *url* belongs to epicurious.com."""
        return cls._DOMAIN in url

    def scrape(self, url: str) -> RecipeData:
        """Fetch *url* and return a populated :class:`RecipeData`."""
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        return RecipeData(
            title=self._parse_title(soup),
            description=self._parse_description(soup),
            ingredients=self._parse_ingredients(soup),
            instructions=self._parse_instructions(soup),
            prep_time=self._parse_time(soup, "preptime"),
            cook_time=self._parse_time(soup, "cooktime"),
            servings=self._parse_servings(soup),
            source_url=url,
        )

    def _parse_title(self, soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find("h1", {"data-testid": "recipe-title"}) or soup.find("h1")
        return tag.get_text(strip=True) if tag else None

    def _parse_description(self, soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find("div", {"class": re.compile(r"dek", re.I)})
        return tag.get_text(strip=True) if tag else None

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all("li", {"data-testid": "IngredientList"})
        if not items:
            items = soup.find_all("li", {"class": re.compile(r"ingredient", re.I)})
        return [li.get_text(strip=True) for li in items if li.get_text(strip=True)]

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all("li", {"class": re.compile(r"step", re.I)})
        return [li.get_text(strip=True) for li in items if li.get_text(strip=True)]

    def _parse_time(self, soup: BeautifulSoup, kind: str) -> Optional[str]:
        tag = soup.find(attrs={"itemprop": kind})
        if tag:
            return tag.get("datetime") or tag.get_text(strip=True)
        return None

    def _parse_servings(self, soup: BeautifulSoup) -> Optional[str]:
        tag = soup.find(attrs={"itemprop": "recipeYield"})
        return tag.get_text(strip=True) if tag else None
