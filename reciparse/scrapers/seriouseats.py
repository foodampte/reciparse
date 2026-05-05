from urllib.parse import urlparse

from bs4 import BeautifulSoup

from reciparse.scrapers.base import BaseScraper, RecipeData


class SeriousEatsScraper(BaseScraper):
    """Scraper for seriouseats.com recipes."""

    DOMAIN = "www.seriouseats.com"

    def supports(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.netloc in (self.DOMAIN, "seriouseats.com")

    def scrape(self, url: str) -> RecipeData:
        response = self._fetch(url)
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
        tag = soup.find("h1", class_="heading__title")
        return tag.get_text(strip=True) if tag else ""

    def _parse_description(self, soup: BeautifulSoup) -> str:
        tag = soup.find("div", class_="section--summary")
        if tag:
            p = tag.find("p")
            return p.get_text(strip=True) if p else tag.get_text(strip=True)
        return ""

    def _parse_ingredients(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all("li", class_="ingredient")
        return [li.get_text(strip=True) for li in items if li.get_text(strip=True)]

    def _parse_instructions(self, soup: BeautifulSoup) -> list[str]:
        items = soup.find_all("li", class_="mntl-sc-block-html")
        if not items:
            items = soup.select(".section--instructions ol li")
        return [li.get_text(strip=True) for li in items if li.get_text(strip=True)]

    def _parse_time(self, soup: BeautifulSoup, kind: str) -> str:
        label_map = {"prep": "Prep", "cook": "Cook"}
        label_text = label_map.get(kind, "")
        for block in soup.find_all("div", class_="project-meta__time-container"):
            label = block.find("span", class_="meta-text__label")
            value = block.find("span", class_="meta-text__data")
            if label and label_text.lower() in label.get_text(strip=True).lower():
                return value.get_text(strip=True) if value else ""
        return ""

    def _parse_servings(self, soup: BeautifulSoup) -> str:
        for block in soup.find_all("div", class_="project-meta__time-container"):
            label = block.find("span", class_="meta-text__label")
            value = block.find("span", class_="meta-text__data")
            if label and "serving" in label.get_text(strip=True).lower():
                return value.get_text(strip=True) if value else ""
        return ""
