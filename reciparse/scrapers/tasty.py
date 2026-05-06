"""Scraper for tasty.co recipes."""

from __future__ import annotations

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from reciparse.scrapers.base import BaseScraper, RecipeData


class TastyScraper(BaseScraper):
    """Scraper for tasty.co."""

    _DOMAIN = "tasty.co"

    @classmethod
    def supports(cls, url: str) -> bool:
        host = urlparse(url).hostname or ""
        return host == cls._DOMAIN or host.endswith("." + cls._DOMAIN)

    def scrape(self, url: str) -> RecipeData:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        return RecipeData(
            title=self._parse_title(soup),
            description=self._parse_description(soup),
            ingredients=self._parse_ingredients(soup),
            instructions=self._parse_instructions(soup),
            prep_time=self._parse_prep_time(soup),
            cook_time=self._parse_cook_time(soup),
            servings=self._parse_servings(soup),
            url=url,
        )

    def _parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("h1", class_="recipe-name")
        if tag:
            return tag.get_text(strip=True)
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            return og["content"].strip()
        return ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find("p", class_="description")
        if tag:
            return tag.get_text(strip=True)
        og = soup.find("meta", property="og:description")
        if og and og.get("content"):
            return og["content"].strip()
        return ""

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        items = soup.select("ul.ingredients li")
        return [li.get_text(strip=True) for li in items if li.get_text(strip=True)]

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        items = soup.select("ol.prep-steps li")
        return [li.get_text(strip=True) for li in items if li.get_text(strip=True)]

    def _parse_prep_time(self, soup: BeautifulSoup) -> str:
        tag = soup.find("dd", class_="prep-time")
        return tag.get_text(strip=True) if tag else ""

    def _parse_cook_time(self, soup: BeautifulSoup) -> str:
        tag = soup.find("dd", class_="cook-time")
        return tag.get_text(strip=True) if tag else ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        tag = soup.find("dd", class_="servings")
        return tag.get_text(strip=True) if tag else ""
