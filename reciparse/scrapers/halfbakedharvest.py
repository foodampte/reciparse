"""Scraper for Half Baked Harvest (halfbakedharvest.com)."""
from __future__ import annotations

import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class HalfBakedHarvestScraper(BaseScraper):
    """Scraper for halfbakedharvest.com recipes."""

    _DOMAIN = "halfbakedharvest.com"

    @staticmethod
    def supports(url: str) -> bool:
        host = urlparse(url).netloc.lower().lstrip("www.")
        return host == "halfbakedharvest.com"

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
            cook_time=self._parse_time(soup, "cook"),
            servings=self._parse_servings(soup),
            source_url=url,
        )

    def _parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("h2", class_=re.compile(r"wprm-recipe-name"))
        if tag:
            return tag.get_text(strip=True)
        og = soup.find("meta", property="og:title")
        return og["content"].strip() if og and og.get("content") else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find(class_=re.compile(r"wprm-recipe-summary"))
        if tag:
            return tag.get_text(separator=" ", strip=True)
        meta = soup.find("meta", attrs={"name": "description"})
        return meta["content"].strip() if meta and meta.get("content") else ""

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all(class_=re.compile(r"wprm-recipe-ingredient$"))
        if items:
            return [li.get_text(separator=" ", strip=True) for li in items]
        return []

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all(class_=re.compile(r"wprm-recipe-instruction-text"))
        if items:
            return [li.get_text(separator=" ", strip=True) for li in items]
        return []

    def _parse_time(self, soup: BeautifulSoup, kind: str) -> str:
        container = soup.find(class_=re.compile(rf"wprm-recipe-{kind}-time-container"))
        if not container:
            return ""
        minutes = container.find(class_=re.compile(rf"wprm-recipe-{kind}_time-minutes"))
        return f"{minutes.get_text(strip=True)} minutes" if minutes else ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        tag = soup.find(class_=re.compile(r"wprm-recipe-servings"))
        if tag:
            return tag.get_text(strip=True)
        return ""
