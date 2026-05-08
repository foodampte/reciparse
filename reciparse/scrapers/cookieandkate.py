"""Scraper for Cookie and Kate (cookieandkate.com)."""
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class CookieAndKateScraper(BaseScraper):
    """Scraper for cookieandkate.com recipes."""

    DOMAIN = "cookieandkate.com"

    @staticmethod
    def supports(url: str) -> bool:
        """Return True if the URL belongs to cookieandkate.com."""
        hostname = urlparse(url).hostname or ""
        return hostname == "cookieandkate.com" or hostname == "www.cookieandkate.com"

    def scrape(self, url: str) -> RecipeData:
        """Fetch and parse a Cookie and Kate recipe page."""
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
        tag = soup.find("h2", class_="wprm-recipe-name")
        if tag:
            return tag.get_text(strip=True)
        tag = soup.find("h1", class_="entry-title")
        return tag.get_text(strip=True) if tag else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find("div", class_="wprm-recipe-summary")
        if tag:
            return tag.get_text(" ", strip=True)
        return ""

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all("li", class_="wprm-recipe-ingredient")
        return [li.get_text(" ", strip=True) for li in items]

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all("div", class_="wprm-recipe-instruction-text")
        return [div.get_text(" ", strip=True) for div in items]

    def _parse_prep_time(self, soup: BeautifulSoup) -> str:
        tag = soup.find("span", class_="wprm-recipe-prep_time-container")
        return tag.get_text(strip=True) if tag else ""

    def _parse_cook_time(self, soup: BeautifulSoup) -> str:
        tag = soup.find("span", class_="wprm-recipe-cook_time-container")
        return tag.get_text(strip=True) if tag else ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        tag = soup.find("span", class_="wprm-recipe-servings-container")
        return tag.get_text(strip=True) if tag else ""
