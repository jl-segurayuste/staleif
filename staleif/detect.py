from __future__ import annotations

import ast

_FLIP_OP = {"Lt": "Gt", "LtE": "GtE", "Gt": "Lt", "GtE": "LtE", "Eq": "Eq"}


def _is_version_info_expr(node: ast.AST) -> bool:
    if isinstance(node, ast.Attribute) and node.attr == "version_info":
        return isinstance(node.value, ast.Name) and node.value.id == "sys"
    if isinstance(node, ast.Subscript):
        return _is_version_info_expr(node.value)
    return False


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
    def __init__(self, if_node: ast.If, op_name: str, threshold: tuple[int, ...]):
        self.if_node = if_node
        self.op_name = op_name
        self.threshold = threshold
        self.has_else = bool(if_node.orelse)


def find_version_guards(tree: ast.Module) -> list[VersionGuard]:
    """Cada `if` cuya condición compara sys.version_info contra una tupla/entero literal."""
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
        elif _is_version_info_expr(right):
            threshold = _version_tuple_from_node(left)
            op_name = _FLIP_OP[op_name]  # "(3,8) <= sys.version_info" -> "version_info >= (3,8)"
        else:
            continue

        if threshold is None:
            continue
        guards.append(VersionGuard(node, op_name, threshold))
    return guards
