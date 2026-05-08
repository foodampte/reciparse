"""Scraper for Smitten Kitchen (smittenkitchen.com)."""
from __future__ import annotations

import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, RecipeData


class SmittenKitchenScraper(BaseScraper):
    """Scraper for smittenkitchen.com recipes."""

    _DOMAIN = "smittenkitchen.com"

    @staticmethod
    def supports(url: str) -> bool:
        host = urlparse(url).netloc.lower().lstrip("www.")
        return host == "smittenkitchen.com"

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
        tag = soup.find("h1", class_="entry-title") or soup.find("h1")
        return tag.get_text(strip=True) if tag else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            return meta["content"].strip()
        intro = soup.find("div", class_="entry-content")
        if intro:
            first_p = intro.find("p")
            return first_p.get_text(strip=True) if first_p else ""
        return ""

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        items: list[str] = []
        container = soup.find("ul", class_=re.compile(r"ingredient", re.I))
        if container:
            items = [li.get_text(strip=True) for li in container.find_all("li")]
        if not items:
            for li in soup.find_all("li"):
                text = li.get_text(strip=True)
                if text:
                    items.append(text)
        return items

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        container = soup.find("ol", class_=re.compile(r"instruction|direction|step", re.I))
        if container:
            return [li.get_text(strip=True) for li in container.find_all("li")]
        return []

    def _parse_time(self, soup: BeautifulSoup, kind: str) -> str | None:
        pattern = re.compile(kind, re.I)
        tag = soup.find(attrs={"class": pattern})
        if tag:
            text = tag.get_text(strip=True)
            match = re.search(r"\d+\s*(?:min|hour|hr)s?", text, re.I)
            return match.group(0) if match else None
        return None

    def _parse_servings(self, soup: BeautifulSoup) -> str | None:
        tag = soup.find(attrs={"class": re.compile(r"serving|yield", re.I)})
        if tag:
            text = tag.get_text(strip=True)
            match = re.search(r"\d+", text)
            return match.group(0) if match else None
        return None
