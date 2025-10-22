import sys
import os
from typing import List, Dict

import streamlit as st

# Ensure repo root is on path (this file is already at repo root, but keep robust for cloud)
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pts_extra.grammar import Grammar
from pts_extra.lr1 import LR1Builder
from pts_extra.parser import LR1Parser


def build_derivation(reductions, grammar: Grammar) -> List[str]:
    if not reductions:
        return []
    derivation = []
    # Start symbol
    derivation.append(grammar.start_symbol)
    for head, body in reversed(reductions):
        body_str = Grammar.EPSILON if body == [Grammar.EPSILON] else " ".join(body)
        derivation.append(f"{head} -> {body_str}")
    return derivation


def format_action_table(builder: LR1Builder) -> List[Dict[str, str]]:
    terminals = sorted(list(builder.aug.terminals | {Grammar.END_MARKER}))
    rows: List[Dict[str, str]] = []
    for state_id in range(len(builder.states)):
        row: Dict[str, str] = {"Estado": str(state_id)}
        for terminal in terminals:
            key = (state_id, terminal)
            if key in builder.action:
                action = builder.action[key]
                if action[0] == 's':
                    row[terminal] = f"s{action[1]}"
                elif action[0] == 'r':
                    head, body = action[1]
                    row[terminal] = f"r({head} -> {' '.join(body) if body else Grammar.EPSILON})"
                elif action[0] == 'acc':
                    row[terminal] = "accept"
            else:
                row[terminal] = ""
        rows.append(row)
    return rows


def format_goto_table(builder: LR1Builder) -> List[Dict[str, str]]:
    nonterminals = sorted(list(builder.aug.nonterminals))
    rows: List[Dict[str, str]] = []
    for state_id in range(len(builder.states)):
        row: Dict[str, str] = {"Estado": str(state_id)}
        for nt in nonterminals:
            key = (state_id, nt)
            row[nt] = str(builder.goto_table[key]) if key in builder.goto_table else ""
        rows.append(row)
    return rows


def format_parse_steps(steps: List[dict]) -> List[Dict[str, str]]:
    formatted = []
    for step in steps:
        if 'stack' in step:
            stack = step['stack']
            input_tokens = step['input']
        else:
            stack = step.get('symbols', [])
            input_tokens = step.get('input', [])
        formatted.append({
            'Pila': ' '.join(str(x) for x in stack),
            'Entrada': ' '.join(str(x) for x in input_tokens),
            'Acción': step.get('action', ''),
        })
    return formatted


def render_states(builder: LR1Builder):
    for state_id, state in enumerate(builder.states):
        with st.expander(f"Estado {state_id}"):
            for item in state:
                rhs = list(item.body)
                rhs.insert(item.dot, '•')
                st.code(f"{item.head} -> {' '.join(rhs)}   |   {item.lookahead}")


# ---------------- UI -----------------
st.set_page_config(page_title="Analizador LR(1)", page_icon="📊", layout="wide")
st.title("Analizador LR(1) • Streamlit")
st.caption("Parser canónico LR(1) con gramáticas en BNF. Ingrese una gramática y una cadena para analizar.")

# Presets
EXAMPLE_GRAMMAR = (
    "E -> E + T | T\n"
    "T -> T * F | F\n"
    "F -> ( E ) | id"
)

col1, col2 = st.columns([3, 2])
with col1:
    grammar_text = st.text_area(
        "Gramática (BNF)",
        value=EXAMPLE_GRAMMAR,
        height=180,
        placeholder="Ejemplo:\nE -> E + T | T\nT -> T * F | F\nF -> ( E ) | id",
    )
with col2:
    input_string = st.text_input("Cadena a analizar", value="id + id * id")
    analyze = st.button("Analizar", type="primary")

if analyze:
    grammar_text = (grammar_text or "").strip()
    input_string = (input_string or "").strip()

    if not grammar_text or not input_string:
        st.error("Por favor proporciona tanto la gramática como la cadena de entrada.")
        st.stop()

    try:
        grammar = Grammar.parse_bnf(grammar_text)
    except Exception as e:
        st.error(f"Error al procesar la gramática: {e}")
        st.stop()

    builder = LR1Builder(grammar)
    try:
        builder.build_tables()
    except Exception as e:
        st.error(f"Error construyendo tablas LR(1): {e}")
        st.stop()

    if builder.conflicts:
        st.error("La gramática tiene conflictos y no es LR(1).")
        with st.expander("Ver conflictos"):
            for c in builder.conflicts:
                st.write("- ", c)
        st.stop()

    # Parse input
    parser = LR1Parser(grammar, builder.action, builder.goto_table)
    tokens = input_string.split()

    try:
        result = parser.parse(tokens)
    except Exception as e:
        st.error(f"Error durante el análisis: {e}")
        st.stop()

    if not result.get('accepted'):
        st.error(result.get('error', 'La cadena no es aceptada por la gramática'))
        with st.expander("Ver pasos del análisis"):
            steps = format_parse_steps(result.get('steps', []))
            if steps:
                st.dataframe(steps, use_container_width=True)
        st.stop()

    # Success
    st.success("Cadena aceptada. La cadena pertenece al lenguaje generado por la gramática.")

    derivation = build_derivation(result.get('reductions', []), grammar)
    action_rows = format_action_table(builder)
    goto_rows = format_goto_table(builder)
    steps = format_parse_steps(result.get('steps', []))

    tabs = st.tabs(["Gramática", "Tabla LR", "Derivación", "Pasos", "Estados"])

    with tabs[0]:
        stats_cols = st.columns(4)
        stats_cols[0].metric("Producciones", sum(len(rhss) for rhss in grammar.productions.values()))
        stats_cols[1].metric("Terminales", len(grammar.terminals | {Grammar.END_MARKER}))
        stats_cols[2].metric("No terminales", len(grammar.nonterminals))
        stats_cols[3].metric("Estados LR(1)", len(builder.states))

        st.subheader("Símbolos terminales")
        st.write(", ".join(sorted(grammar.terminals | {Grammar.END_MARKER})))
        st.subheader("Símbolos no terminales")
        st.write(", ".join(sorted(grammar.nonterminals)))

    with tabs[1]:
        st.markdown("#### Tabla ACTION")
        st.dataframe(action_rows, use_container_width=True)
        st.markdown("#### Tabla GOTO")
        st.dataframe(goto_rows, use_container_width=True)

    with tabs[2]:
        if derivation:
            for i, step in enumerate(derivation, start=1):
                st.write(f"{i}. {step}")
        else:
            st.info("No se pudo construir la derivación.")

    with tabs[3]:
        if steps:
            st.dataframe(steps, use_container_width=True)
        else:
            st.info("No hay pasos para mostrar.")

    with tabs[4]:
        render_states(builder)

else:
    st.info("Ingrese la gramática y la cadena, luego presione Analizar.")
