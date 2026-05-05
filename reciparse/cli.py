"""Command-line interface for reciparse."""

import sys
import argparse
from typing import Optional

from reciparse.scrapers.registry import ScraperRegistry, UnsupportedSiteError
from reciparse.output.formatters import JSONFormatter
from reciparse.output.csv_formatter import CSVFormatter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reciparse",
        description="Scrape and normalize recipe data from popular cooking sites.",
    )
    parser.add_argument(
        "url",
        help="URL of the recipe page to scrape.",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        metavar="N",
        help="JSON indentation level (default: 2). Ignored for CSV.",
    )
    return parser


def run(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    registry = ScraperRegistry()

    try:
        scraper = registry.get_scraper(args.url)
    except UnsupportedSiteError as exc:
        print(f"reciparse: error: {exc}", file=sys.stderr)
        return 1

    try:
        recipe = scraper.scrape(args.url)
    except Exception as exc:  # noqa: BLE001
        print(f"reciparse: failed to scrape URL: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        formatter = JSONFormatter(indent=args.indent)
    else:
        formatter = CSVFormatter()

    output = formatter.format_one(recipe)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(output)
        except OSError as exc:
            print(f"reciparse: could not write to file: {exc}", file=sys.stderr)
            return 1
    else:
        print(output)

    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
