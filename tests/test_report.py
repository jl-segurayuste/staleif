from staleif.plugin import Finding
from staleif.report import to_console, to_json


def test_to_console_sin_hallazgos():
    out = to_console([])
    assert "No se encontraron" in out


def test_to_console_con_hallazgos_sin_emojis():
    findings = [
        Finding(
            path="a.py",
            line=5,
            verdict="if_dead",
            condition="sys.version_info < (3, 8)",
            detail="ya no aplica",
            commit="abc12345",
            author="Jose",
            summary="workaround viejo",
        )
    ]
    out = to_console(findings)
    assert "IF MUERTO" in out
    assert "a.py:5" in out
    assert "abc12345" in out
    assert "🔧" not in out and "⚠" not in out


def test_to_json_valido():
    findings = [Finding(path="a.py", line=1, verdict="if_dead", condition="x")]
    out = to_json(findings)
    assert '"path": "a.py"' in out
