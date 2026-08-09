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


def test_tupla_completa_sin_subindice_tiene_projection_none():
    tree = ast.parse("import sys\nif sys.version_info < (3, 8):\n    pass\n")
    guards = find_version_guards(tree)
    assert guards[0].projection is None


def test_subindice_0_tiene_projection_1():
    # Bug real encontrado 2026-08-09: "sys.version_info[0]" solo mira el
    # componente mayor, así que su `projection` debe ser 1 -- no None (tupla
    # completa), o se compararía contra minor/micro que ese subíndice ni
    # siquiera lee.
    tree = ast.parse("import sys\nif sys.version_info[0] > 3:\n    pass\n")
    guards = find_version_guards(tree)
    assert guards[0].projection == 1


def test_slice_hasta_2_tiene_projection_2():
    tree = ast.parse("import sys\nif sys.version_info[:2] < (3, 6):\n    pass\n")
    guards = find_version_guards(tree)
    assert guards[0].projection == 2


def test_subindice_con_variable_se_ignora():
    tree = ast.parse("import sys\ni = 0\nif sys.version_info[i] < 3:\n    pass\n")
    assert find_version_guards(tree) == []


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
