from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class MinimalistBakerScraper(BaseScraper):
    """Scraper for minimalistbaker.com recipes."""

    DOMAIN = "minimalistbaker.com"

    @classmethod
    def supports(cls, url: str) -> bool:
        host = urlparse(url).netloc.lower().lstrip("www.")
        return host == cls.DOMAIN

    def scrape(self, url: str) -> RecipeData:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        return RecipeData(
            url=url,
            title=self._parse_title(soup),
            description=self._parse_description(soup),
            ingredients=self._parse_ingredients(soup),
            instructions=self._parse_instructions(soup),
            prep_time=self._parse_prep_time(soup),
            cook_time=self._parse_cook_time(soup),
            servings=self._parse_servings(soup),
        )

    def _parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("h2", class_="wprm-recipe-name") or soup.find("h1", class_="entry-title")
        return tag.get_text(strip=True) if tag else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find(class_="wprm-recipe-summary")
        return tag.get_text(strip=True) if tag else ""

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all(class_="wprm-recipe-ingredient")
        if not items:
            items = soup.find_all("li", class_="ingredient")
        return [item.get_text(separator=" ", strip=True) for item in items]

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all(class_="wprm-recipe-instruction-text")
        if not items:
            items = soup.find_all("li", class_="instruction")
        return [item.get_text(strip=True) for item in items]

    def _parse_prep_time(self, soup: BeautifulSoup) -> str:
        tag = soup.find(class_="wprm-recipe-prep_time-container")
        return tag.get_text(strip=True) if tag else ""

    def _parse_cook_time(self, soup: BeautifulSoup) -> str:
        tag = soup.find(class_="wprm-recipe-cook_time-container")
        return tag.get_text(strip=True) if tag else ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        tag = soup.find(class_="wprm-recipe-servings-container")
        return tag.get_text(strip=True) if tag else ""
