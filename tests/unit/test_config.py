import json

import pytest

from books.config import CatalogConfig, load_config
from books.exceptions import ConfigError
from books.models import MAX_YEAR, MIN_YEAR


def test_default_config():
    assert load_config() == CatalogConfig(MIN_YEAR, MAX_YEAR)


def test_environment_overrides_defaults(monkeypatch):
    monkeypatch.setenv("BOOKS_MIN_YEAR", "1900")
    monkeypatch.setenv("BOOKS_MAX_YEAR", "2000")

    config = load_config()

    assert config.min_year == 1900
    assert config.max_year == 2000


def test_invalid_environment_value_raises(monkeypatch):
    monkeypatch.setenv("BOOKS_MIN_YEAR", "abc")

    with pytest.raises(ConfigError, match="integer") as exc_info:
        load_config()

    assert isinstance(exc_info.value.__cause__, ValueError)


def test_min_year_greater_than_max_year_raises(monkeypatch):
    monkeypatch.setenv("BOOKS_MIN_YEAR", "2000")
    monkeypatch.setenv("BOOKS_MAX_YEAR", "1900")

    with pytest.raises(ConfigError, match="exceed"):
        load_config()


def test_config_from_file(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps({"min_year": 1800, "max_year": 1990}), encoding="utf-8"
    )

    assert load_config(path) == CatalogConfig(1800, 1990)


def test_environment_overrides_file(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps({"min_year": 1800, "max_year": 1990}), encoding="utf-8"
    )
    monkeypatch.setenv("BOOKS_MAX_YEAR", "1950")

    assert load_config(path) == CatalogConfig(1800, 1950)


def test_missing_config_file_raises(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "missing.json")


def test_invalid_json_config_raises(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{bad json", encoding="utf-8")

    with pytest.raises(ConfigError, match="Invalid JSON"):
        load_config(path)


def test_non_object_json_config_raises(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("[1, 2]", encoding="utf-8")

    with pytest.raises(ConfigError, match="object"):
        load_config(path)