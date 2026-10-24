from unittest.mock import Mock, create_autospec

import pytest

from books.config import CatalogConfig
from books.exceptions import BookValidationError, EmptyCatalogError, ExportError
from books.protocols import BookRepository, ReportExporter
from books.services import BookCatalog, ReportService


def test_publish_exports_all_books(sample_books, tmp_path):
    repository = Mock(spec=BookRepository)
    repository.list_all.return_value = sample_books
    exporter = Mock(spec=ReportExporter)
    target = tmp_path / "report.json"

    count = ReportService(repository, exporter).publish(target)

    assert count == 4
    exporter.export.assert_called_once_with(sample_books, target)


def test_publish_empty_catalog_does_not_call_exporter(tmp_path):
    repository = Mock(spec=BookRepository)
    repository.list_all.return_value = []
    exporter = Mock(spec=ReportExporter)

    with pytest.raises(EmptyCatalogError):
        ReportService(repository, exporter).publish(tmp_path / "r.json")

    exporter.export.assert_not_called()


def test_export_failure_is_wrapped_with_cause(sample_books, tmp_path):
    repository = Mock(spec=BookRepository)
    repository.list_all.return_value = sample_books
    exporter = Mock(spec=ReportExporter)
    exporter.export.side_effect = OSError("disk full")

    with pytest.raises(ExportError, match="Export failed") as exc_info:
        ReportService(repository, exporter).publish(tmp_path / "r.json")

    assert isinstance(exc_info.value.__cause__, OSError)


def test_repeated_publish_uses_side_effect_sequence(sample_books, tmp_path):
    repository = Mock(spec=BookRepository)
    repository.list_all.side_effect = [[], sample_books]
    exporter = Mock(spec=ReportExporter)
    service = ReportService(repository, exporter)

    with pytest.raises(EmptyCatalogError):
        service.publish(tmp_path / "r.json")
    assert service.publish(tmp_path / "r.json") == 4
    assert repository.list_all.call_count == 2


def test_catalog_add_calls_repository(book_factory):
    repository = Mock(spec=BookRepository)
    book = book_factory()

    BookCatalog(repository).add(book)

    repository.add.assert_called_once_with(book)


def test_invalid_year_does_not_reach_repository(book_factory):
    repository = Mock(spec=BookRepository)
    catalog = BookCatalog(repository, CatalogConfig(1900, 2000))

    with pytest.raises(BookValidationError):
        catalog.add(book_factory(year=1840))

    repository.add.assert_not_called()


def test_repository_failure_propagates(book_factory):
    repository = Mock(spec=BookRepository)
    repository.add.side_effect = RuntimeError("db down")

    with pytest.raises(RuntimeError, match="db down"):
        BookCatalog(repository).add(book_factory())


def test_autospec_detects_wrong_signature():
    exporter = create_autospec(ReportExporter, instance=True)

    with pytest.raises(TypeError):
        exporter.export(1, 2, 3)