# Contribuir

## Ampliar la detección

`staleif/detect.py` reconoce comparaciones contra `sys.version_info`
(directo o `[0]`/subíndice) frente a una tupla/entero literal. Si quieres
añadir soporte para otra forma de comprobar versión (p.ej.
`platform.python_version_tuple()`), añade el reconocimiento en
`_is_version_info_expr` y su test correspondiente en `tests/test_detect.py`.

La lógica de "¿esto ya es inalcanzable?" vive aparte, en
`staleif/verlogic.py::branch_verdict` — no mezclar la detección de AST con
la lógica de veredicto.

## Antes de un PR

- `ruff check .` y `pytest` en verde.
- Todo cambio en `verlogic.py` necesita tests para los 4 operadores
  (`<`, `<=`, `>`, `>=`) en los 3 casos (vivo, if muerto, else muerto).
