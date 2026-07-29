from staleif.verlogic import branch_verdict


def test_lt_if_dead_cuando_min_ya_lo_supera():
    # sys.version_info < (3, 8), min_version = (3, 11) -> nunca es verdad
    assert branch_verdict("Lt", (3, 8), (3, 11)) == "if_dead"


def test_lt_live_cuando_min_es_menor():
    assert branch_verdict("Lt", (3, 12), (3, 11)) == "live"


def test_lte_if_dead_cuando_min_supera_estrictamente():
    assert branch_verdict("LtE", (3, 8), (3, 11)) == "if_dead"


def test_lte_live_cuando_min_es_igual():
    assert branch_verdict("LtE", (3, 11), (3, 11)) == "live"


def test_gte_else_dead_cuando_min_ya_lo_cumple():
    assert branch_verdict("GtE", (3, 8), (3, 11)) == "else_dead"


def test_gte_live_cuando_min_no_lo_cumple():
    assert branch_verdict("GtE", (3, 12), (3, 11)) == "live"


def test_gt_else_dead_cuando_min_supera_estrictamente():
    assert branch_verdict("Gt", (3, 8), (3, 11)) == "else_dead"


def test_gt_live_cuando_min_es_igual():
    assert branch_verdict("Gt", (3, 11), (3, 11)) == "live"


def test_eq_nunca_se_marca():
    assert branch_verdict("Eq", (3, 8), (3, 11)) == "live"


def test_tuplas_de_longitud_distinta_se_normalizan():
    # sys.version_info[0] < 3, min_version = (3, 11) -> False siempre (3 >= 3)
    assert branch_verdict("Lt", (3,), (3, 11)) == "if_dead"
