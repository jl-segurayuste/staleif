from __future__ import annotations

import ast
import subprocess
from pathlib import Path

from staleif.blame import blame_line
from staleif.detect import find_version_guards
from staleif.plugin import Finding
from staleif.pyver import project_min_python_version
from staleif.verlogic import branch_verdict

_OP_SYMBOL = {"Lt": "<", "LtE": "<=", "Gt": ">", "GtE": ">="}


def _tracked_python_files(repo_path: Path) -> list[Path] | None:
    result = subprocess.run(
        ["git", "ls-files", "*.py"], cwd=repo_path, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return None
    return [repo_path / line for line in result.stdout.splitlines() if line]


def analyze_repo(repo_path: Path) -> list[Finding] | None:
    """None si no hay `requires-python` declarado (no aplica) o si no es un repo git."""
    min_version = project_min_python_version(repo_path)
    if min_version is None:
        return None

    files = _tracked_python_files(repo_path)
    if files is None:
        return None

    findings: list[Finding] = []
    for path in files:
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue

        rel = str(path.relative_to(repo_path))
        for guard in find_version_guards(tree):
            verdict = branch_verdict(guard.op_name, guard.threshold, min_version)
            if verdict == "live":
                continue
            if verdict == "else_dead" and not guard.has_else:
                continue  # no hay rama else que sea codigo muerto

            condition = f"sys.version_info {_OP_SYMBOL[guard.op_name]} {guard.threshold}"
            lineno = guard.if_node.lineno
            blame = blame_line(repo_path, rel, lineno) or {}

            if verdict == "if_dead":
                detail = (
                    f"El proyecto ya requiere Python >= {'.'.join(map(str, min_version))}, "
                    "así que esta condición nunca es verdadera -- la rama 'if' es inalcanzable."
                )
            else:
                detail = (
                    f"El proyecto ya requiere Python >= {'.'.join(map(str, min_version))}, "
                    "así que esta condición siempre es verdadera -- la rama 'else' es inalcanzable."
                )

            findings.append(
                Finding(
                    path=rel,
                    line=lineno,
                    verdict=verdict,
                    condition=condition,
                    detail=detail,
                    commit=blame.get("commit"),
                    author=blame.get("author"),
                    summary=blame.get("summary"),
                )
            )

    return findings
