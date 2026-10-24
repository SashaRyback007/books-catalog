"""CSV import каталогу."""

import csv
from pathlib import Path

from books.exceptions import CatalogImportError
from books.models import Book

REQUIRED_COLUMNS = ("title", "author", "year", "pages")


def _parse_row(row: dict, line: int) -> Book:
    try:
        return Book(
            title=row["title"],
            author=row["author"],
            year=int(row["year"]),
            pages=int(row["pages"]),
        )
    except (ValueError, TypeError) as error:
        raise CatalogImportError(
            f"Line {line}: invalid record", line=line
        ) from error


def import_books_csv(path: str | Path) -> list[Book]:
    path = Path(path)
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames or []
            missing = [c for c in REQUIRED_COLUMNS if c not in fields]
            if missing:
                raise CatalogImportError(
                    f"Missing columns: {', '.join(missing)}"
                )
            return [
                _parse_row(row, line)
                for line, row in enumerate(reader, start=2)
            ]
    except FileNotFoundError as error:
        raise CatalogImportError(f"File not found: {path}") from error