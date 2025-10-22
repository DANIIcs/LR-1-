# LR(1) Analyzer (Python + Streamlit/Flask)

This repository contains:

- `pts_extra/`: Core LR(1) implementation (Grammar parser, LR(1) builder, shift-reduce parser)
- `streamlit_app.py`: Streamlit UI to build LR(1) tables, analyze strings, and visualize derivations and automaton states
- `webapp/`: Legacy Flask web UI (kept for reference)

## Run with Streamlit (recommended)

Requires Python 3.10+.

```powershell
# From the repo root
python -m venv .venv ; .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app will be available at http://localhost:8501

### Try a Grammar
Paste this BNF and analyze the string `id + id * id`:

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

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Create a new app on https://streamlit.io/cloud and point it to your repo.
3. Set the entrypoint to `streamlit_app.py` (default) and branch `main`.
4. Deployment uses `requirements.txt` automatically.

## (Optional) Run the Flask UI

```powershell
# From the repo root
python -m venv .venv ; .venv\Scripts\Activate.ps1
pip install flask
python webapp\app.py
```

App will be available at http://127.0.0.1:5000

## CLI Sanity Test
Quick check from the repo root:

```powershell
python - <<'PY'
from pts_extra.grammar import Grammar
from pts_extra.lr1 import LR1Builder
from pts_extra.parser import LR1Parser
g = Grammar.parse_bnf('E -> E + T | T\nT -> id')
b = LR1Builder(g)
b.build_tables()
p = LR1Parser(g, b.action, b.goto_table)
result = p.parse(['id'])
print('Parse accepted:', result['accepted'])
PY
```

Expected output:

```
Parse accepted: True
```

## Notes
- Streamlit app is the primary UI now. Flask app remains for reference, styles, and templates.
- If you change Python files while the Streamlit app is running, it auto-reloads.
