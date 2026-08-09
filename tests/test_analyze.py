from conftest import commit_all, write

from staleif.analyze import analyze_repo


def _init_project(repo, requires_python):
    write(repo, "pyproject.toml", f'[project]\nname="x"\nrequires-python="{requires_python}"\n')


def test_guarda_muerta_se_detecta_con_blame(git_repo):
    _init_project(git_repo, ">=3.11")
    write(
        git_repo,
        "compat.py",
        "import sys\n\ndef foo():\n    if sys.version_info < (3, 8):\n        return 'old'\n    return 'new'\n",
    )
    commit_all(git_repo, "workaround para python viejo")

    findings = analyze_repo(git_repo)
    assert len(findings) == 1
    f = findings[0]
    assert f.verdict == "if_dead"
    assert f.path == "compat.py"
    assert f.summary == "workaround para python viejo"
    assert f.commit is not None


def test_guarda_viva_no_se_marca(git_repo):
    _init_project(git_repo, ">=3.8")
    write(
        git_repo,
        "compat.py",
        "import sys\nif sys.version_info < (3, 12):\n    x = 1\nelse:\n    x = 2\n",
    )
    commit_all(git_repo)
    assert analyze_repo(git_repo) == []


def test_else_muerto_se_detecta(git_repo):
    _init_project(git_repo, ">=3.11")
    write(
        git_repo,
        "compat.py",
        "import sys\nif sys.version_info >= (3, 8):\n    x = 1\nelse:\n    x = 2\n",
    )
    commit_all(git_repo)
    findings = analyze_repo(git_repo)
    assert len(findings) == 1
    assert findings[0].verdict == "else_dead"


def test_sin_else_no_marca_else_dead(git_repo):
    _init_project(git_repo, ">=3.11")
    write(git_repo, "compat.py", "import sys\nif sys.version_info >= (3, 8):\n    x = 1\n")
    commit_all(git_repo)
    assert analyze_repo(git_repo) == []


def test_sin_requires_python_devuelve_none(git_repo):
    write(git_repo, "pyproject.toml", '[project]\nname="x"\n')
    write(git_repo, "compat.py", "import sys\nif sys.version_info < (3, 8):\n    pass\n")
    commit_all(git_repo)
    assert analyze_repo(git_repo) is None


def test_subindice_0_no_se_confunde_con_tupla_completa(git_repo):
    # Bug real encontrado 2026-08-09: "sys.version_info[0] > 3" solo mira el
    # mayor, pero se comparaba contra el min_version COMPLETO ("3.8" con
    # requires-python ">=3.8"), así que "[0] > 3" parecía "siempre verdadero"
    # por culpa del "8" -- un componente que esa comparación ni siquiera lee.
    # Eso marcaba la rama "else" (que sí se ejecuta en Python 3.8) como código
    # muerto. Con la proyección correcta (solo el componente 0 cuenta), la
    # rama "else" sigue siendo alcanzable y no debe marcarse.
    _init_project(git_repo, ">=3.8")
    write(
        git_repo,
        "compat.py",
        "import sys\nif sys.version_info[0] > 3:\n    x = 1\nelse:\n    x = 2\n",
    )
    commit_all(git_repo)
    assert analyze_repo(git_repo) == []


def test_subindice_0_guarda_realmente_muerta_se_sigue_detectando(git_repo):
    _init_project(git_repo, ">=3.11")
    write(
        git_repo,
        "compat.py",
        "import sys\nif sys.version_info[0] < 3:\n    x = 1\n",
    )
    commit_all(git_repo)
    findings = analyze_repo(git_repo)
    assert len(findings) == 1
    assert findings[0].verdict == "if_dead"


def test_slice_guarda_muerta_se_detecta(git_repo):
    _init_project(git_repo, ">=3.11")
    write(
        git_repo,
        "compat.py",
        "import sys\nif sys.version_info[:2] < (3, 6):\n    x = 1\n",
    )
    commit_all(git_repo)
    findings = analyze_repo(git_repo)
    assert len(findings) == 1
    assert findings[0].verdict == "if_dead"


def test_subindice_micro_sin_suelo_fiable_se_abstiene(git_repo):
    # requires-python ">=3.8" solo da mayor.menor -- no hay suelo fiable para
    # el componente micro ("[2]"), así que no se puede razonar con seguridad
    # y hay que abstenerse en vez de adivinar.
    _init_project(git_repo, ">=3.8")
    write(
        git_repo,
        "compat.py",
        "import sys\nif sys.version_info[2] < 5:\n    x = 1\n",
    )
    commit_all(git_repo)
    assert analyze_repo(git_repo) == []


def test_fichero_con_syntaxerror_se_ignora_sin_romper(git_repo):
    _init_project(git_repo, ">=3.11")
    write(git_repo, "roto.py", "esto no es python valido [[[")
    write(git_repo, "compat.py", "import sys\nif sys.version_info < (3, 8):\n    pass\n")
    commit_all(git_repo)
    findings = analyze_repo(git_repo)
    assert len(findings) == 1
    assert findings[0].path == "compat.py"
