from conftest import commit_all, write

from staleif.cli import main


def test_scan_sin_requires_python_exit_0(git_repo, capsys):
    write(git_repo, "a.py", "x = 1\n")
    commit_all(git_repo)
    rc = main(["scan", str(git_repo)])
    assert rc == 0
    assert "No aplica" in capsys.readouterr().out


def test_scan_con_guarda_muerta_exit_1_si_fail_on_found(git_repo, capsys):
    write(git_repo, "pyproject.toml", '[project]\nname="x"\nrequires-python=">=3.11"\n')
    write(git_repo, "compat.py", "import sys\nif sys.version_info < (3, 8):\n    pass\n")
    commit_all(git_repo)
    rc = main(["scan", str(git_repo), "--fail-on-found"])
    assert rc == 1


def test_scan_sin_guardas_muertas_exit_0(git_repo, capsys):
    write(git_repo, "pyproject.toml", '[project]\nname="x"\nrequires-python=">=3.8"\n')
    write(git_repo, "compat.py", "import sys\nif sys.version_info < (3, 12):\n    pass\n")
    commit_all(git_repo)
    rc = main(["scan", str(git_repo), "--fail-on-found"])
    assert rc == 0


def test_scan_json(git_repo, capsys):
    write(git_repo, "pyproject.toml", '[project]\nname="x"\nrequires-python=">=3.11"\n')
    write(git_repo, "compat.py", "import sys\nif sys.version_info < (3, 8):\n    pass\n")
    commit_all(git_repo)
    main(["scan", str(git_repo), "--json"])
    out = capsys.readouterr().out
    assert '"path"' in out
