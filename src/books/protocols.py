"""Інтерфейси залежностей."""

from pathlib import Path
from typing import Protocol

from books.models import Book


class BookRepository(Protocol):
    def add(self, book: Book) -> None:
        ...

    def list_all(self) -> list[Book]:
        ...


class ReportExporter(Protocol):
    def export(self, books: list[Book], path: Path) -> None:
        ...