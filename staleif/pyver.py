from __future__ import annotations

import tomllib
from pathlib import Path

from packaging.specifiers import SpecifierSet
from packaging.version import Version


def min_python_version(requires_python: str) -> tuple[int, ...] | None:
    """Versión mínima (X, Y) a partir de un 'requires-python' tipo '>=3.11,<4'.
    None si no hay ninguna cota inferior (>=/>)."""
    try:
        specifiers = SpecifierSet(requires_python)
    except Exception:  # noqa: BLE001 -- requires-python puede tener sintaxis rara
        return None

    candidates: list[tuple[int, ...]] = []
    for spec in specifiers:
        if spec.operator in (">=", ">"):
            try:
                v = Version(spec.version)
            except Exception:  # noqa: BLE001, S112 -- version rara en el specifier, se ignora
                continue
            candidates.append(v.release[:2])

    if not candidates:
        return None
    return max(candidates)


def project_min_python_version(repo_path: Path) -> tuple[int, ...] | None:
    pyproject = repo_path / "pyproject.toml"
    if not pyproject.exists():
        return None
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError:
        return None
    requires_python = data.get("project", {}).get("requires-python")
    if not requires_python:
        return None
    return min_python_version(requires_python)
