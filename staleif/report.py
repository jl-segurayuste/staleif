from __future__ import annotations

import json

from staleif.plugin import Finding

_LABEL = {"if_dead": "IF MUERTO", "else_dead": "ELSE MUERTO"}


def to_console(findings: list[Finding]) -> str:
    if not findings:
        return "No se encontraron guardas de versión muertas."

    lines = []
    for f in findings:
        lines.append(f"[{_LABEL[f.verdict]}] {f.path}:{f.line} -- {f.condition}")
        lines.append(f"           {f.detail}")
        if f.commit:
            short = f.commit[:8]
            author = f.author or "?"
            summary = f.summary or ""
            lines.append(f"           Añadido en {short} por {author}: \"{summary}\"")
        lines.append("")

    lines.append(f"Total: {len(findings)} guarda(s) de versión muerta(s).")
    return "\n".join(lines)


def to_json(findings: list[Finding]) -> str:
    return json.dumps([f.model_dump() for f in findings], ensure_ascii=False, indent=2)
