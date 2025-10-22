from __future__ import annotations
from flask import Flask, render_template, request
from typing import List, Dict, Tuple
import os, sys

# Ensure repo root is on sys.path so we can import lr1_py when running with -m
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pts_extra.grammar import Grammar
from pts_extra.lr1 import LR1Builder
from pts_extra.parser import LR1Parser
from pts_extra.lexer import tokenize_expr, tokens_from_space_separated

app = Flask(__name__)

EXPR_GRAMMAR = """
# Gramática de expresiones aritméticas (LR(1))
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
""".strip()


def compute_tables_for_template(builder: LR1Builder):
    # Terminales (incluyendo $)
    terminals = sorted(list(builder.aug.terminals | {Grammar.END_MARKER}))
    nonterminals = sorted(list(builder.aug.nonterminals))
    # ACTION y GOTO como matrices por estado
    action_rows = []
    for s in range(len(builder.states)):
        row = []
        for a in terminals:
            val = builder.action.get((s, a))
            row.append(val)
        action_rows.append((s, row))
    goto_rows = []
    for s in range(len(builder.states)):
        row = []
        for A in nonterminals:
            val = builder.goto_table.get((s, A))
            row.append(val)
        goto_rows.append((s, row))
    return terminals, nonterminals, action_rows, goto_rows


def derive_sentential_forms(start_symbol: str, reductions: List[Tuple[str, List[str]]]) -> List[List[str]]:
    """
    Reconstruye una derivación (aproximación a la derivación por la derecha) a partir de las reducciones
    realizadas por el parser LR, aplicándolas en orden inverso.
    """
    forms: List[List[str]] = [[start_symbol]]
    w = [start_symbol]
    for head, body in reversed(reductions):
        # Reemplazar la ocurrencia más a la derecha de head por body
        try:
            idx = len(w) - 1 - w[::-1].index(head)
        except ValueError:
            # Si no se encuentra, intentamos la primera ocurrencia (mejor esfuerzo)
            try:
                idx = w.index(head)
            except ValueError:
                continue
        replacement = [] if body == [Grammar.EPSILON] else body
        w = w[:idx] + replacement + w[idx + 1 :]
        forms.append(w[:])
    return forms


@app.route('/', methods=['GET', 'POST'])
def index():
    grammar_text = EXPR_GRAMMAR
    input_text = 'id + id * id'
    mode = 'lex'
    result = None
    tables = None
    conflicts = []

    if request.method == 'POST':
        grammar_text = request.form.get('grammar', '').strip() or EXPR_GRAMMAR
        input_text = request.form.get('input', '').strip()
        mode = request.form.get('mode', 'lex')
        try:
            g = Grammar.parse_bnf(grammar_text)
            builder = LR1Builder(g)
            builder.build_tables()
            parser = LR1Parser(builder.aug, builder.action, builder.goto_table)
            tokens = tokenize_expr(input_text) if mode == 'lex' else tokens_from_space_separated(input_text)
            result = parser.parse(tokens)
            terminals, nonterminals, action_rows, goto_rows = compute_tables_for_template(builder)
            tables = {
                'terminals': terminals,
                'nonterminals': nonterminals,
                'action_rows': action_rows,
                'goto_rows': goto_rows,
            }
            conflicts = builder.conflicts
            # Derivación aproximada desde las reducciones
            derivation = derive_sentential_forms(builder.aug.start_symbol, result.get('reductions', [])) if result else []
        except Exception as e:
            return render_template('index.html', error=str(e),
                                   grammar=grammar_text, input_text=input_text, mode=mode)
        return render_template('index.html',
                               grammar=grammar_text,
                               input_text=input_text,
                               mode=mode,
                               tables=tables,
                               result=result,
                               derivation=derivation,
                               conflicts=conflicts)

    return render_template('index.html', grammar=grammar_text, input_text=input_text, mode=mode)


def create_app():
    return app


if __name__ == '__main__':
    app.run(debug=True)
