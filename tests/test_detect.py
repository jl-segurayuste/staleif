import ast

from staleif.detect import find_version_guards


def test_detecta_lt_tupla():
    tree = ast.parse("import sys\nif sys.version_info < (3, 8):\n    pass\n")
    guards = find_version_guards(tree)
    assert len(guards) == 1
    assert guards[0].op_name == "Lt"
    assert guards[0].threshold == (3, 8)


def test_detecta_gte_tupla():
    tree = ast.parse("import sys\nif sys.version_info >= (3, 10):\n    pass\n")
    guards = find_version_guards(tree)
    assert guards[0].op_name == "GtE"
    assert guards[0].threshold == (3, 10)


def test_detecta_comparacion_invertida():
    tree = ast.parse("import sys\nif (3, 8) <= sys.version_info:\n    pass\n")
    guards = find_version_guards(tree)
    assert len(guards) == 1
    assert guards[0].op_name == "GtE"  # (3,8) <= v  equivale a  v >= (3,8)
    assert guards[0].threshold == (3, 8)


def test_detecta_subscript_indice_0():
    tree = ast.parse("import sys\nif sys.version_info[0] < 3:\n    pass\n")
    guards = find_version_guards(tree)
    assert guards[0].threshold == (3,)


def test_detecta_presencia_de_else():
    tree = ast.parse("import sys\nif sys.version_info < (3, 8):\n    pass\nelse:\n    pass\n")
    guards = find_version_guards(tree)
    assert guards[0].has_else is True


def test_sin_else_has_else_false():
    tree = ast.parse("import sys\nif sys.version_info < (3, 8):\n    pass\n")
    guards = find_version_guards(tree)
    assert guards[0].has_else is False


def test_if_normal_no_se_detecta():
    tree = ast.parse("if x > 5:\n    pass\n")
    assert find_version_guards(tree) == []


def test_comparacion_con_variable_no_literal_se_ignora():
    tree = ast.parse("import sys\nlimite = (3, 8)\nif sys.version_info < limite:\n    pass\n")
    assert find_version_guards(tree) == []
