"""Scraper for 101cookbooks.com."""

from __future__ import annotations

import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class HundredAndOneCookbooksScraper(BaseScraper):
    """Scraper for 101cookbooks.com recipes."""

    DOMAIN = "101cookbooks.com"

    @staticmethod
    def supports(url: str) -> bool:
        host = urlparse(url).netloc.lstrip("www.")
        return host == "101cookbooks.com"

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
            prep_time=self._parse_time(soup, "prep"),
            cook_time=self._parse_time(soup, "cook"),
            servings=self._parse_servings(soup),
        )

    def _parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("h1", class_=re.compile(r"recipe.*title|title.*recipe", re.I))
        if not tag:
            tag = soup.find("h1")
        return tag.get_text(strip=True) if tag else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find("div", class_=re.compile(r"recipe.*description|description", re.I))
        if not tag:
            tag = soup.find("meta", attrs={"name": "description"})
            return tag.get("content", "").strip() if tag else ""
        return tag.get_text(strip=True)

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        container = soup.find("ul", class_=re.compile(r"ingredient", re.I))
        if not container:
            container = soup.find("div", class_=re.compile(r"ingredient", re.I))
        if not container:
            return []
        return [li.get_text(strip=True) for li in container.find_all("li") if li.get_text(strip=True)]

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        container = soup.find("ol", class_=re.compile(r"instruction|direction|step", re.I))
        if not container:
            container = soup.find("div", class_=re.compile(r"instruction|direction", re.I))
        if not container:
            return []
        items = container.find_all("li")
        return [li.get_text(strip=True) for li in items if li.get_text(strip=True)]

    def _parse_time(self, soup: BeautifulSoup, kind: str) -> str:
        tag = soup.find(attrs={"class": re.compile(kind + r"[_-]?time", re.I)})
        return tag.get_text(strip=True) if tag else ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        tag = soup.find(attrs={"class": re.compile(r"serving|yield", re.I)})
        return tag.get_text(strip=True) if tag else ""
