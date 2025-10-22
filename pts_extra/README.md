# Estructura estilo "continua" (Python)

Este directorio replica la estructura de tus evaluaciones continuas, en Python, reutilizando el núcleo LR(1) de `lr1_py/`.

- `token.py` — clase Token mínima.
- `scanner.py` — `Scanner` y `ejecutar_scanner`, genera `inputs/<archivo>_tokens.txt`.
- `parser_lr1.py` — construcción del parser LR(1) (usa `lr1_py`).
- `main.py` — punto de entrada CLI (similar a `main.cpp`).
- `run_all_inputs.py` — corre `main.py` sobre `inputs/input1..5.txt` y guarda resultados en `outputs/`.
- `inputs/`, `outputs/` — mismas carpetas operativas.

## Ejecutar un archivo

```powershell
D:/Principal/compiladores/puntosextra/.venv/Scripts/python.exe -m pts_extra.main pts_extra/inputs/input1.txt
```

## Procesar todos

```powershell
D:/Principal/compiladores/puntosextra/.venv/Scripts/python.exe pts_extra/run_all_inputs.py
```

Puedes pasar una gramática BNF personalizada como segundo argumento a `main`.
