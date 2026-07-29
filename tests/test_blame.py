from conftest import commit_all, write

from staleif.blame import blame_line


def test_blame_line_devuelve_info_del_commit(git_repo):
    write(git_repo, "mod.py", "x = 1\ny = 2\n")
    commit_all(git_repo, "añade x e y")
    info = blame_line(git_repo, "mod.py", 1)
    assert info is not None
    assert "commit" in info
    assert info.get("summary") == "añade x e y"


def test_blame_line_fichero_inexistente(git_repo):
    assert blame_line(git_repo, "no-existe.py", 1) is None


def test_blame_line_distingue_lineas_de_commits_distintos(git_repo):
    write(git_repo, "mod.py", "x = 1\n")
    commit_all(git_repo, "primero")
    write(git_repo, "mod.py", "x = 1\ny = 2\n")
    commit_all(git_repo, "segundo")

    info1 = blame_line(git_repo, "mod.py", 1)
    info2 = blame_line(git_repo, "mod.py", 2)
    assert info1["summary"] == "primero"
    assert info2["summary"] == "segundo"
