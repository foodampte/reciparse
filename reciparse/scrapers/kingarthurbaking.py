import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class KingArthurBakingScraper(BaseScraper):
    """Scraper for King Arthur Baking (kingarthurbaking.com)."""

    DOMAIN = "kingarthurbaking.com"

    @staticmethod
    def supports(url: str) -> bool:
        host = urlparse(url).netloc.lower().lstrip("www.")
        return host == "kingarthurbaking.com"

    def scrape(self, url: str) -> RecipeData:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        return RecipeData(
            title=self._parse_title(soup),
            description=self._parse_description(soup),
            ingredients=self._parse_ingredients(soup),
            instructions=self._parse_instructions(soup),
            prep_time=self._parse_time(soup, "prep"),
            cook_time=self._parse_time(soup, "bake"),
            servings=self._parse_servings(soup),
            url=url,
        )

    def _parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("h1", class_=re.compile(r"recipe.*title|title.*recipe", re.I))
        if tag is None:
            tag = soup.find("h1")
        return tag.get_text(strip=True) if tag else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find("div", class_=re.compile(r"recipe.*description|description.*recipe", re.I))
        if tag is None:
            tag = soup.find("meta", attrs={"name": "description"})
            return tag.get("content", "").strip() if tag else ""
        return tag.get_text(strip=True)

    def _parse_ingredients(self, soup: BeautifulSoup) -> list:
        section = soup.find("ul", class_=re.compile(r"ingredient", re.I))
        if section is None:
            return []
        return [li.get_text(strip=True) for li in section.find_all("li") if li.get_text(strip=True)]

    def _parse_instructions(self, soup: BeautifulSoup) -> list:
        section = soup.find("ol", class_=re.compile(r"instruction|direction|step", re.I))
        if section is None:
            section = soup.find("div", class_=re.compile(r"instruction|direction", re.I))
        if section is None:
            return []
        items = section.find_all("li")
        if items:
            return [li.get_text(strip=True) for li in items if li.get_text(strip=True)]
        return [p.get_text(strip=True) for p in section.find_all("p") if p.get_text(strip=True)]

    def _parse_time(self, soup: BeautifulSoup, kind: str) -> str:
        tag = soup.find(attrs={"data-time-type": re.compile(kind, re.I)})
        if tag is None:
            tag = soup.find(class_=re.compile(rf"{kind}.*time|time.*{kind}", re.I))
        return tag.get_text(strip=True) if tag else ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        tag = soup.find(class_=re.compile(r"yield|serving", re.I))
        return tag.get_text(strip=True) if tag else ""
