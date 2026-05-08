# Registry Update: SkinnyTaste Scraper

The `SkinnyTasteScraper` has been added to the project. To activate it, ensure
the following import and registration are present in
`reciparse/scrapers/registry.py`:

```python
from .skinnytaste import SkinnyTasteScraper

# Inside ScraperRegistry._register_defaults:
self.register(SkinnyTasteScraper())
```

## Supported domains

- `skinnytaste.com`
- `www.skinnytaste.com`

## Parsed fields

| Field          | CSS / class selector                          |
|----------------|-----------------------------------------------|
| `title`        | `h2.wprm-recipe-name` or `h1.entry-title`     |
| `description`  | `div.wprm-recipe-summary`                     |
| `ingredients`  | `li.wprm-recipe-ingredient`                   |
| `instructions` | `div.wprm-recipe-instruction-text`            |
| `prep_time`    | `span.wprm-recipe-prep_time-container`        |
| `cook_time`    | `span.wprm-recipe-cook_time-container`        |
| `servings`     | `span.wprm-recipe-servings-container`         |

SkinnyTaste uses the **WPRM (WP Recipe Maker)** plugin, so the selectors are
stable across most recipe pages on the site.
