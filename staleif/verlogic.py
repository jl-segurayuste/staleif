from __future__ import annotations


def _pad(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)), b + (0,) * (n - len(b))


def branch_verdict(op_name: str, threshold: tuple[int, ...], min_version: tuple[int, ...]) -> str:
    """'if_dead' | 'else_dead' | 'live'.

    Dado que la versión de Python en ejecución siempre es >= min_version
    (por `requires-python`), decide si la comparación `sys.version_info <op>
    threshold` puede seguir siendo verdadera o falsa alguna vez, o si ya
    está decidida para siempre.
    """
    t, m = _pad(threshold, min_version)

    if op_name == "Lt":
        return "if_dead" if m >= t else "live"
    if op_name == "LtE":
        return "if_dead" if m > t else "live"
    if op_name == "Gt":
        return "else_dead" if m > t else "live"
    if op_name == "GtE":
        return "else_dead" if m >= t else "live"
    return "live"  # Eq (y cualquier otro): ambiguo, no se marca
