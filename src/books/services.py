"""Бізнес-логіка каталогу книг."""

from pathlib import Path

from books.config import CatalogConfig
from books.exceptions import BookValidationError, EmptyCatalogError, ExportError
from books.models import Book
from books.protocols import BookRepository, ReportExporter


class BookCatalog:
    def __init__(
        self,
        repository: BookRepository,
        config: CatalogConfig | None = None,
    ) -> None:
        self._repository = repository
        self._config = config or CatalogConfig()

    def add(self, book: Book) -> None:
        low, high = self._config.min_year, self._config.max_year
        if not low <= book.year <= high:
            raise BookValidationError(
                "year", f"must be between {low} and {high}"
            )
        self._repository.add(book)

    def all(self) -> list[Book]:
        return list(self._repository.list_all())

    def find_by_author(self, author: str) -> list[Book]:
        needle = author.strip().casefold()
        return [b for b in self.all() if needle in b.author.casefold()]

    def find_by_title(self, title: str) -> list[Book]:
        needle = title.strip().casefold()
        return [b for b in self.all() if needle in b.title.casefold()]

    def filter_by_year(self, start: int, end: int) -> list[Book]:
        if start > end:
            raise ValueError("start year must not exceed end year")
        return [b for b in self.all() if start <= b.year <= end]

    def largest_by_pages(self) -> Book:
        books = self.all()
        if not books:
            raise EmptyCatalogError("Catalog is empty")
        return max(books, key=lambda book: book.pages)

    def average_pages(self) -> float:
        books = self.all()
        if not books:
            raise EmptyCatalogError("Catalog is empty")
        return sum(book.pages for book in books) / len(books)


class ReportService:
    def __init__(
        self,
        repository: BookRepository,
        exporter: ReportExporter,
    ) -> None:
        self._repository = repository
        self._exporter = exporter

    def publish(self, path: Path) -> int:
        books = self._repository.list_all()
        if not books:
            raise EmptyCatalogError("Catalog is empty")
        try:
            self._exporter.export(books, path)
        except OSError as error:
            raise ExportError(f"Export failed: {error}") from error
        return len(books)