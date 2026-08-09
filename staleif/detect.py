from __future__ import annotations

import ast

_FLIP_OP = {"Lt": "Gt", "LtE": "GtE", "Gt": "Lt", "GtE": "LtE", "Eq": "Eq"}


def _is_version_info_expr(node: ast.AST) -> bool:
    if isinstance(node, ast.Attribute) and node.attr == "version_info":
        return isinstance(node.value, ast.Name) and node.value.id == "sys"
    if isinstance(node, ast.Subscript):
        return _is_version_info_expr(node.value)
    return False


def _projection_from_node(node: ast.AST) -> int | None:
    """Si `node` es `sys.version_info` sin subíndice, devuelve None (compara la
    tupla entera). Si es `sys.version_info[N]` (índice entero literal), devuelve
    N+1 -- el número de componentes iniciales que de verdad importan para esta
    comparación ("[0]" solo mira el mayor, así que solo el componente 0 cuenta).
    Si es `sys.version_info[:N]`, igualmente devuelve N. Cualquier otra forma de
    subíndice (variable, slice con paso, índice negativo...) devuelve -1: "no se
    puede razonar con seguridad", para que el llamador se abstenga en vez de
    adivinar -- ver el bug real de `sys.version_info[0] > 3` en el docstring del
    módulo."""
    if isinstance(node, ast.Attribute):
        return None  # sys.version_info sin subíndice: tupla completa
    if not isinstance(node, ast.Subscript):
        return -1
    sl = node.slice
    if isinstance(sl, ast.Constant) and isinstance(sl.value, int) and sl.value >= 0:
        return sl.value + 1
    if isinstance(sl, ast.Slice) and sl.lower is None and sl.step is None:
        if sl.upper is None:
            return None  # "[:]" -- equivale a la tupla completa
        if isinstance(sl.upper, ast.Constant) and isinstance(sl.upper.value, int):
            return sl.upper.value
    return -1


def _version_tuple_from_node(node: ast.AST) -> tuple[int, ...] | None:
    if isinstance(node, ast.Tuple):
        values = []
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, int):
                values.append(elt.value)
            else:
                return None
        return tuple(values)
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return (node.value,)
    return None


class VersionGuard:
    def __init__(
        self, if_node: ast.If, op_name: str, threshold: tuple[int, ...], projection: int | None
    ):
        self.if_node = if_node
        self.op_name = op_name
        self.threshold = threshold
        self.has_else = bool(if_node.orelse)
        # Cuántos componentes iniciales de sys.version_info mira de verdad esta
        # comparación -- None si mira la tupla entera (sin subíndice). Ver
        # `_projection_from_node`: sin esto, "sys.version_info[0] > 3" se trataba
        # como si comparase la tupla completa, produciendo un veredicto REAL
        # incorrecto (marcaba como muerta una rama else que sí se ejecuta) en
        # cuanto el `requires-python` del proyecto incluía un minor -- ej.
        # ">=3.8" hacía que "[0] > 3" pareciera "siempre verdadero" por culpa
        # del "8" de min_version, que ese subíndice ni siquiera mira.
        self.projection = projection


def find_version_guards(tree: ast.Module) -> list[VersionGuard]:
    """Cada `if` cuya condición compara sys.version_info (o un subíndice/slice
    reconocible del mismo, ej. `[0]`/`[:2]`) contra una tupla/entero literal."""
    guards: list[VersionGuard] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not isinstance(test, ast.Compare) or len(test.ops) != 1:
            continue

        left, op, right = test.left, test.ops[0], test.comparators[0]
        op_name = type(op).__name__
        if op_name not in _FLIP_OP:
            continue

        if _is_version_info_expr(left):
            threshold = _version_tuple_from_node(right)
            projection = _projection_from_node(left)
        elif _is_version_info_expr(right):
            threshold = _version_tuple_from_node(left)
            op_name = _FLIP_OP[op_name]  # "(3,8) <= sys.version_info" -> "version_info >= (3,8)"
            projection = _projection_from_node(right)
        else:
            continue

        if threshold is None or projection == -1:
            continue
        guards.append(VersionGuard(node, op_name, threshold, projection))
    return guards
