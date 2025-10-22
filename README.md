# LR(1) Analyzer (Python + Flask)

This repository contains:

- `pts_extra/`: Core LR(1) implementation (Grammar parser, LR(1) builder, shift-reduce parser)
- `webapp/`: Flask web UI to build LR(1) tables, analyze strings, and visualize derivations and automaton states
- `continua/`: Original C++ continuous evaluation code (kept intact)

## Run the Web UI (Windows PowerShell)

```powershell
# From the repo root
D:\Principal\compiladores\puntosextra\.venv\Scripts\python.exe D:\Principal\compiladores\puntosextra\webapp\app.py
# App will be available at http://127.0.0.1:5000
```

If you prefer, activate the venv and run from the `webapp` folder:

```powershell
# Optional: activate venv
D:\Principal\compiladores\puntosextra\.venv\Scripts\Activate.ps1

# Then
cd D:\Principal\compiladores\puntosextra\webapp
python app.py
```

## Try a Grammar
Paste this BNF into the UI and analyze the string `id + id * id`:

```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

The UI shows:
- ACTION and GOTO tables
- Automaton states with LR(1) items
- Step-by-step parsing trace
- A compact derivation sequence

## CLI Sanity Test
Quick check from the repo root:

```powershell
D:\Principal\compiladores\puntosextra\.venv\Scripts\python.exe -c "from pts_extra.grammar import Grammar; from pts_extra.lr1 import LR1Builder; from pts_extra.parser import LR1Parser; g = Grammar.parse_bnf('E -> E + T | T\nT -> id'); b = LR1Builder(g); b.build_tables(); p = LR1Parser(g, b.action, b.goto_table); result = p.parse(['id', '+', 'id']); print('Parse result:', result['accepted'])"
```

Expected output:
```
Parse result: True
```

## Notes
- The web template is `webapp/templates/index.html` and uses `webapp/static/style_new.css`.
- If you change Python files while the app is running, Flask auto-reloads in debug mode.
- If you see a 404 for `/favicon.ico`, it is harmless and can be ignored.
