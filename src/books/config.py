"""Конфігурація допустимого діапазону років."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

from books.exceptions import ConfigError
from books.models import MAX_YEAR, MIN_YEAR

ENV_MIN_YEAR = "BOOKS_MIN_YEAR"
ENV_MAX_YEAR = "BOOKS_MAX_YEAR"


@dataclass(frozen=True, slots=True)
class CatalogConfig:
    min_year: int = MIN_YEAR
    max_year: int = MAX_YEAR


def _to_int(name: str, value: object) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise ConfigError(f"{name} must be an integer: {value!r}") from error


def _read_file(path: Path) -> dict:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ConfigError(f"Config file not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ConfigError(f"Invalid JSON in config: {path}") from error
    if not isinstance(raw, dict):
        raise ConfigError("Config must be a JSON object")
    return raw


def load_config(path: str | Path | None = None) -> CatalogConfig:
    """Defaults < JSON-файл < environment variables."""
    min_year, max_year = MIN_YEAR, MAX_YEAR

    if path is not None:
        raw = _read_file(Path(path))
        min_year = _to_int("min_year", raw.get("min_year", min_year))
        max_year = _to_int("max_year", raw.get("max_year", max_year))

    env_min = os.getenv(ENV_MIN_YEAR)
    if env_min is not None:
        min_year = _to_int(ENV_MIN_YEAR, env_min)
    env_max = os.getenv(ENV_MAX_YEAR)
    if env_max is not None:
        max_year = _to_int(ENV_MAX_YEAR, env_max)

    if min_year > max_year:
        raise ConfigError("min_year must not exceed max_year")
    return CatalogConfig(min_year, max_year)