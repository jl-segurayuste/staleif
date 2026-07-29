from __future__ import annotations

import subprocess
from pathlib import Path


def blame_line(repo_path: Path, relpath: str, lineno: int) -> dict[str, str] | None:
    """Autor/commit/resumen de la línea `lineno` de `relpath`, vía `git blame`."""
    result = subprocess.run(
        ["git", "blame", "-L", f"{lineno},{lineno}", "--porcelain", "--", relpath],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout:
        return None

    lines = result.stdout.splitlines()
    info: dict[str, str] = {"commit": lines[0].split()[0]}
    for line in lines[1:]:
        if line.startswith("author "):
            info["author"] = line[len("author ") :]
        elif line.startswith("author-time "):
            info["author_time"] = line[len("author-time ") :]
        elif line.startswith("summary "):
            info["summary"] = line[len("summary ") :]
    return info
