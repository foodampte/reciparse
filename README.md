# reciparse

A CLI tool that scrapes and normalizes recipe data from popular cooking sites into structured JSON or CSV.

---

## Installation

```bash
pip install reciparse
```

Or install from source:

```bash
git clone https://github.com/yourusername/reciparse.git
cd reciparse
pip install .
```

---

## Usage

Scrape a recipe and output as JSON:

```bash
reciparse https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/
```

Save output to a file:

```bash
reciparse https://www.foodnetwork.com/recipes/some-recipe --format csv --output recipe.csv
```

### Output Example

```json
{
  "title": "Best Chocolate Chip Cookies",
  "ingredients": ["2 1/4 cups flour", "1 tsp baking soda", "..."],
  "instructions": ["Preheat oven to 375°F", "Mix dry ingredients", "..."],
  "prep_time": "15 minutes",
  "cook_time": "10 minutes",
  "servings": 48
}
```

### Supported Sites

- AllRecipes
- Food Network
- Epicurious
- Serious Eats
- BBC Good Food

---

## Options

| Flag | Description |
|------|-------------|
| `--format` | Output format: `json` (default) or `csv` |
| `--output` | Save to a file instead of stdout |
| `--pretty` | Pretty-print JSON output |

---

## License

This project is licensed under the [MIT License](LICENSE).