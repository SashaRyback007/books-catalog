import json
from dataclasses import asdict

import pytest

import books.exporters as exporters_module
from books.exporters import JsonBookExporter
from books.models import Book


def test_json_export_writes_valid_json(tmp_path, sample_books):
    output = tmp_path / "books.json"

    JsonBookExporter().export(sample_books, output)

    data = json.loads(output.read_text(encoding="utf-8"))
    assert data == [asdict(book) for book in sample_books]
    assert len(data) == 4


def test_json_export_keeps_cyrillic_readable(tmp_path):
    output = tmp_path / "books.json"
    book = Book("Кобзар", "Тарас Шевченко", 1840, 240)

    JsonBookExporter().export([book], output)

    text = output.read_text(encoding="utf-8")
    assert "Кобзар" in text
    assert "\\u" not in text


def test_json_export_of_empty_list(tmp_path):
    output = tmp_path / "books.json"

    JsonBookExporter().export([], output)

    assert json.loads(output.read_text(encoding="utf-8")) == []


def test_json_export_overwrites_existing_file(tmp_path, sample_books):
    output = tmp_path / "books.json"
    output.write_text("old", encoding="utf-8")

    JsonBookExporter().export(sample_books[:1], output)

    assert len(json.loads(output.read_text(encoding="utf-8"))) == 1


def test_no_temporary_file_after_success(tmp_path, sample_books):
    output = tmp_path / "books.json"

    JsonBookExporter().export(sample_books, output)

    assert not (tmp_path / "books.json.tmp").exists()


def test_failed_export_keeps_old_file_and_removes_temporary(
    tmp_path, sample_books, monkeypatch
):
    output = tmp_path / "books.json"
    output.write_text("old valid data", encoding="utf-8")

    def broken_replace(source, target):
        raise OSError("replace failed")

    monkeypatch.setattr(exporters_module.os, "replace", broken_replace)

    with pytest.raises(OSError, match="replace failed"):
        JsonBookExporter().export(sample_books, output)

    assert output.read_text(encoding="utf-8") == "old valid data"
    assert not (tmp_path / "books.json.tmp").exists()