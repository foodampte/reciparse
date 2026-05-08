import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class ThePioneerWomanScraper(BaseScraper):
    """Scraper for thepioneerwoman.com recipes."""

    DOMAIN = "thepioneerwoman.com"

    @staticmethod
    def supports(url: str) -> bool:
        host = urlparse(url).hostname or ""
        return host == "www.thepioneerwoman.com" or host == "thepioneerwoman.com"

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
            source_url=url,
        )

    def _parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("h1", class_=re.compile(r"recipe-title|heading", re.I))
        if tag:
            return tag.get_text(strip=True)
        og = soup.find("meta", property="og:title")
        return og["content"].strip() if og and og.get("content") else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find("div", class_=re.compile(r"recipe-description|intro", re.I))
        if tag:
            return tag.get_text(strip=True)
        meta = soup.find("meta", attrs={"name": "description"})
        return meta["content"].strip() if meta and meta.get("content") else ""

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        container = soup.find("ul", class_=re.compile(r"ingredient", re.I))
        if container:
            return [li.get_text(strip=True) for li in container.find_all("li") if li.get_text(strip=True)]
        return []

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        container = soup.find("ol", class_=re.compile(r"direction|instruction|step", re.I))
        if container:
            return [li.get_text(strip=True) for li in container.find_all("li") if li.get_text(strip=True)]
        return []

    def _parse_prep_time(self, soup: BeautifulSoup) -> str:
        tag = soup.find(attrs={"data-label": re.compile(r"prep", re.I)})
        return tag.get_text(strip=True) if tag else ""

    def _parse_cook_time(self, soup: BeautifulSoup) -> str:
        tag = soup.find(attrs={"data-label": re.compile(r"cook", re.I)})
        return tag.get_text(strip=True) if tag else ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        tag = soup.find(attrs={"data-label": re.compile(r"serv|yield", re.I)})
        return tag.get_text(strip=True) if tag else ""
