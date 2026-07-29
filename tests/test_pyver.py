from conftest import write

from staleif.pyver import min_python_version, project_min_python_version


def test_min_python_version_simple():
    assert min_python_version(">=3.11") == (3, 11)


def test_min_python_version_con_cota_superior():
    assert min_python_version(">=3.8,<4") == (3, 8)


def test_min_python_version_toma_la_mas_alta_si_hay_varias():
    assert min_python_version(">=3.8,>=3.10") == (3, 10)


def test_min_python_version_sin_cota_inferior():
    assert min_python_version("<4") is None


def test_min_python_version_sintaxis_invalida():
    assert min_python_version("no es un specifier valido !!!") is None


def test_project_min_python_version_lee_pyproject(git_repo):
    write(git_repo, "pyproject.toml", '[project]\nname="x"\nrequires-python=">=3.10"\n')
    assert project_min_python_version(git_repo) == (3, 10)


def test_project_min_python_version_sin_fichero(git_repo):
    assert project_min_python_version(git_repo) is None


def test_project_min_python_version_sin_requires_python(git_repo):
    write(git_repo, "pyproject.toml", '[project]\nname="x"\n')
    assert project_min_python_version(git_repo) is None
