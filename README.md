# staleif

Encuentra bloques `if sys.version_info < (X, Y):` que ya son código muerto
— porque el propio `requires-python` del proyecto hace tiempo que dejó de
soportar versiones tan viejas — con el contexto de git blame de cuándo y
por qué se añadieron.

```
$ staleif scan .

[IF MUERTO] compat.py:12 -- sys.version_info < (3, 8)
           El proyecto ya requiere Python >= 3.11, así que esta condición
           nunca es verdadera -- la rama 'if' es inalcanzable.
           Añadido en a1b2c3d4 por Jose: "workaround para python 3.7"

Total: 1 guarda(s) de versión muerta(s).
```

## Por qué existe

Los "workarounds" condicionados a la versión de Python son de los tipos de
código muerto más fáciles de dejar olvidados: se añaden con buena razón, el
proyecto sube su `requires-python` mínimo con el tiempo, y nadie vuelve a
por el `if` que ya nunca se ejecuta. A diferencia de detectar código muerto
en general (funciones/imports sin usar), esto es 100% mecánico: si el
proyecto ya no soporta la versión que el `if` comprueba, la rama es
matemáticamente inalcanzable — no hace falta ninguna heurística.

## Instalación

Todavía no está en PyPI:

```bash
pip install git+https://github.com/jl-segurayuste/staleif.git
```

## Uso

```bash
staleif scan .
staleif scan . --json
staleif scan . --fail-on-found   # código de salida 1 si hay alguna
```

Lee el `requires-python` de `pyproject.toml`, recorre los ficheros `.py`
rastreados por git buscando comparaciones contra `sys.version_info` (vía
`ast`, no regex), y usa `git blame` para mostrar cuándo y por qué se
introdujo cada guarda que ya es código muerto.

## Qué NO detecta (todavía)

- Comparaciones contra `__version__` de paquetes de terceros (ver
  [depweight](https://github.com/jl-segurayuste/depweight)/
  [depexplain](https://github.com/jl-segurayuste/depexplain) para el
  ángulo de dependencias).
- `platform.python_version_tuple()` u otras formas no literales de
  comprobar la versión.
- Comparaciones con `==` (ambiguas: podrían seguir aplicando a una versión
  exacta dentro del rango soportado).

## Desarrollo

```bash
pip install -e ".[dev]"
ruff check .
pytest
```
