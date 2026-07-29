from __future__ import annotations

from pydantic import BaseModel


class Finding(BaseModel):
    path: str
    line: int
    verdict: str  # "if_dead" | "else_dead"
    condition: str
    detail: str = ""
    commit: str | None = None
    author: str | None = None
    summary: str | None = None
