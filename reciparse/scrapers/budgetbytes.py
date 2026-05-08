import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class BudgetBytesScraper(BaseScraper):
    """Scraper for budgetbytes.com recipes."""

    DOMAIN = "budgetbytes.com"

    @staticmethod
    def supports(url: str) -> bool:
        host = urlparse(url).hostname or ""
        return host == "budgetbytes.com" or host == "www.budgetbytes.com"

    def scrape(self, url: str) -> RecipeData:
        response = requests.get(url, timeout=10, headers={"User-Agent": "reciparse/1.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        return RecipeData(
            url=url,
            title=self._parse_title(soup),
            description=self._parse_description(soup),
            ingredients=self._parse_ingredients(soup),
            instructions=self._parse_instructions(soup),
            prep_time=self._parse_time(soup, "prep"),
            cook_time=self._parse_time(soup, "cook"),
            servings=self._parse_servings(soup),
        )

    def _parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("h1", class_=re.compile(r"wprm-recipe-name"))
        if tag:
            return tag.get_text(strip=True)
        tag = soup.find("h1", class_="entry-title")
        return tag.get_text(strip=True) if tag else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find(class_=re.compile(r"wprm-recipe-summary"))
        return tag.get_text(strip=True) if tag else ""

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all(class_=re.compile(r"wprm-recipe-ingredient$"))
        if items:
            return [i.get_text(" ", strip=True) for i in items]
        items = soup.find_all("li", class_=re.compile(r"ingredient"))
        return [i.get_text(" ", strip=True) for i in items]

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all(class_=re.compile(r"wprm-recipe-instruction-text"))
        if items:
            return [i.get_text(strip=True) for i in items]
        items = soup.find_all("li", class_=re.compile(r"instruction"))
        return [i.get_text(strip=True) for i in items]

    def _parse_time(self, soup: BeautifulSoup, kind: str) -> str:
        tag = soup.find(class_=re.compile(rf"wprm-recipe-{kind}-time-container"))
        return tag.get_text(" ", strip=True) if tag else ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        tag = soup.find(class_=re.compile(r"wprm-recipe-servings-with-unit"))
        return tag.get_text(strip=True) if tag else ""
