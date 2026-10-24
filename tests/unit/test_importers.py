import pytest

from books.exceptions import CatalogImportError
from books.importers import import_books_csv


def test_import_valid_csv(books_csv):
    books = import_books_csv(books_csv)

    assert len(books) == 4
    assert books[0].title == "Kobzar"
    assert books[0].year == 1840
    assert books[3].pages == 380


def test_import_header_only_returns_empty_list(tmp_path):
    path = tmp_path / "books.csv"
    path.write_text("title,author,year,pages\n", encoding="utf-8")

    assert import_books_csv(path) == []


def test_import_cyrillic_utf8(tmp_path):
    path = tmp_path / "books.csv"
    path.write_text(
        "title,author,year,pages\nКобзар,Тарас Шевченко,1840,240\n",
        encoding="utf-8",
    )

    assert import_books_csv(path)[0].author == "Тарас Шевченко"


@pytest.mark.parametrize(
    "row",
    [
        pytest.param("Book,Author,abc,100", id="year-not-number"),
        pytest.param("Book,Author,1999,xyz", id="pages-not-number"),
        pytest.param("Book,Author,1999,-5", id="negative-pages"),
        pytest.param("Book,Author,1200,100", id="year-out-of-range"),
        pytest.param(",Author,1999,100", id="empty-title"),
        pytest.param("Book,Author,1999", id="missing-value"),
    ],
)
def test_malformed_record_raises_with_line_number(tmp_path, row):
    path = tmp_path / "books.csv"
    path.write_text("title,author,year,pages\n" + row + "\n", encoding="utf-8")

    with pytest.raises(CatalogImportError, match="Line 2") as exc_info:
        import_books_csv(path)

    assert exc_info.value.line == 2


def test_import_error_keeps_original_cause(tmp_path):
    path = tmp_path / "books.csv"
    path.write_text(
        "title,author,year,pages\nBook,Author,abc,100\n", encoding="utf-8"
    )

    with pytest.raises(CatalogImportError) as exc_info:
        import_books_csv(path)

    assert isinstance(exc_info.value.__cause__, ValueError)


def test_missing_file_raises(tmp_path):
    with pytest.raises(CatalogImportError, match="not found") as exc_info:
        import_books_csv(tmp_path / "missing.csv")

    assert isinstance(exc_info.value.__cause__, FileNotFoundError)


def test_missing_columns_raises(tmp_path):
    path = tmp_path / "books.csv"
    path.write_text("title,author\nBook,Author\n", encoding="utf-8")

    with pytest.raises(CatalogImportError, match="Missing columns"):
        import_books_csv(path)