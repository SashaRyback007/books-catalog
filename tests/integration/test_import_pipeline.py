import json

import pytest

from books.exporters import JsonBookExporter
from books.importers import import_books_csv
from books.exceptions import CatalogImportError
from books.repositories import InMemoryBookRepository
from books.services import BookCatalog

pytestmark = pytest.mark.integration


def test_import_search_export(books_csv, tmp_path):
    repository = InMemoryBookRepository()
    catalog = BookCatalog(repository)
    for book in import_books_csv(books_csv):
        catalog.add(book)

    found = catalog.find_by_author("ivan")
    output = tmp_path / "found.json"
    JsonBookExporter().export(found, output)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert [item["title"] for item in data] == ["Zakhar Berkut", "Tyhrolovy"]
    assert catalog.average_pages() == pytest.approx(237.5)


def test_malformed_csv_stops_pipeline_without_output(tmp_path):
    source = tmp_path / "books.csv"
    source.write_text(
        "title,author,year,pages\nKobzar,Taras Shevchenko,1840,abc\n",
        encoding="utf-8",
    )
    output = tmp_path / "result.json"

    with pytest.raises(CatalogImportError):
        books = import_books_csv(source)
        JsonBookExporter().export(books, output)

    assert not output.exists()