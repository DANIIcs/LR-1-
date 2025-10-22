import sys
import os
from typing import List, Dict

import streamlit as st
import streamlit.components.v1 as components
# Ensure repo root is on path (this file is already at repo root, but keep robust for cloud)
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pts_extra.grammar import Grammar
from pts_extra.lr1 import LR1Builder
from pts_extra.parser import LR1Parser
from pts_extra.automata import construir_automata_lr1, render_automata_svg_interactivo, render_afn_items_lr1

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


def render_lr1_items_columns(builder):
    """
    Muestra los ítems LR(1) agrupados por símbolo, en formato de columnas.
    """
    st.markdown("### 📘 Elementos LR(1) por símbolo (en columnas)")

    # Agrupar ítems por cabeza (head)
    grupos = {}
    for state in builder.states:
        for item in state:
            grupos.setdefault(item.head, []).append(item)

    # Crear 3 columnas si hay 3 no terminales, ajustar dinámicamente
    num_cols = min(4, len(grupos))
    cols = st.columns(num_cols)

    heads = sorted(grupos.keys())

    for i, head in enumerate(heads):
        with cols[i % num_cols]:
            st.markdown(
                f"<div style='background-color:#111;padding:10px;border-radius:10px;'>"
                f"<h4 style='color:#00BFFF;text-align:center;margin-bottom:6px;'>{head}</h4>"
                f"<hr style='border:1px solid #333;margin:4px 0;'>",
                unsafe_allow_html=True
            )

            html_items = ""
            for item in grupos[head]:
                rhs = list(item.body)
                rhs.insert(item.dot, "•")
                rhs_str = " ".join(rhs)
                lookaheads = ", ".join(sorted(item.lookahead))
                html_items += (
                    f"<div style='font-family:Consolas,monospace;"
                    f"margin:2px 0;padding:2px 5px;"
                    f"background-color:#1a1a1a;border-radius:5px;'>"
                    f"<span style='color:#FFF;'>{item.head} → {rhs_str}</span> "
                    f"<span style='color:#00FFAA'>, {lookaheads}</span>"
                    f"</div>"
                )

            st.markdown(html_items + "</div>", unsafe_allow_html=True)
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
        first = grammar.compute_first()
        follow = grammar.compute_follow()
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

    tabs = st.tabs(["Gramática", "Tabla de derivación", "Ampliación LR1", "Pasos", "Estados","Automatas"])

    with tabs[0]:
        st.markdown("## 📘 Resumen de la Gramática")
        st.divider()

        # --- Tarjetas métricas principales ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Producciones", sum(len(rhss) for rhss in grammar.productions.values()))
        col2.metric("Terminales", len(grammar.terminals | {Grammar.END_MARKER}))
        col3.metric("No terminales", len(grammar.nonterminals))
        col4.metric("Estados LR(1)", len(builder.states))

        st.markdown("---")

        # --- Bloques laterales: símbolos terminales y no terminales ---
        st.markdown("### 🔹 Símbolos principales")

        col_t, col_nt = st.columns(2)

        # --- Terminales ---
        with col_t:
            terminales_html = "".join([
                f"<code style='background-color:#222;padding:3px 8px;border-radius:6px;"
                f"margin:3px;display:inline-block;color:#FFD700;'>{t}</code>"
                for t in sorted(grammar.terminals | {Grammar.END_MARKER})
            ])
            st.markdown(
                f"<b style='color:#FFD700;'>Terminales</b><br>"
                f"<div style='font-family:Consolas,monospace;font-size:13px;margin-top:6px;'>{terminales_html}</div>",
                unsafe_allow_html=True
            )

        # --- No terminales ---
        with col_nt:
            no_terminales_html = "".join([
                f"<code style='background-color:#222;padding:3px 8px;border-radius:6px;"
                f"margin:3px;display:inline-block;color:#00BFFF;'>{nt}</code>"
                for nt in sorted(grammar.nonterminals)
            ])
            st.markdown(
                f"<b style='color:#00BFFF;'>No terminales</b><br>"
                f"<div style='font-family:Consolas,monospace;font-size:13px;margin-top:6px;'>{no_terminales_html}</div>",
                unsafe_allow_html=True
            )

        st.markdown("---")

        # --- FIRST y FOLLOW uno al lado del otro ---
        st.markdown("### 🧩 Conjuntos FIRST y FOLLOW")
        col_first, col_follow = st.columns(2)
        with col_first:
            st.markdown("##### FIRST")
            st.markdown(
                "<div style='font-family:Consolas,monospace;font-size:13px;'>"
                + "<br>".join([
                    f"<code>{nt}</code> = {{ {', '.join(sorted(f))} }}"
                    for nt, f in sorted(first.items())
                ])
                + "</div>", unsafe_allow_html=True
            )
        with col_follow:
            st.markdown("##### FOLLOW")
            st.markdown(
                "<div style='font-family:Consolas,monospace;font-size:13px;'>"
                + "<br>".join([
                    f"<code>{nt}</code> = {{ {', '.join(sorted(f))} }}"
                    for nt, f in sorted(follow.items())
                ])
                + "</div>", unsafe_allow_html=True
            )

        st.markdown("---")

        # --- Producciones con fondo tipo código ---
        st.markdown("### 📜 Producciones")
        st.markdown(
            "<div style='font-family:Consolas,monospace;font-size:14px;"
            "background-color:#1e1e1e;border-radius:8px;padding:10px;'>"
            + "<br>".join(
                [f"<code>{head} → {' '.join(body)}</code>" for head, bodies in grammar.productions.items() for body in
                 bodies]
            )
            + "</div>",
            unsafe_allow_html=True
        )

    with tabs[1]:
        st.markdown("#### Tabla ACTION")
        st.dataframe(action_rows, use_container_width=True)
        st.markdown("#### Tabla GOTO")
        st.dataframe(goto_rows, use_container_width=True)

    with tabs[2]:
        if derivation:
            st.markdown("### Derivación paso a paso")
            derivation_table = []
            for i, step in enumerate(derivation, start=1):
                derivation_table.append({"Paso": i, "Producción": step})
            st.dataframe(derivation_table, use_container_width=True)

            # ---------------- NUEVA SECCIÓN: Ítems agrupados por símbolo ----------------
            st.markdown("### Elementos LR(1) agrupados por símbolo")

            grupos = {}
            for state in builder.states:
                for item in state:
                    grupos.setdefault(item.head, []).append(item)

            num_cols = min(4, len(grupos))
            cols = st.columns(num_cols)

            for i, (head, items) in enumerate(sorted(grupos.items())):
                with cols[i % num_cols]:
                    st.markdown(
                        f"<div style='background-color:#111;padding:10px;border-radius:10px;'>"
                        f"<h4 style='color:#00BFFF;text-align:center;margin-bottom:6px;'>{head}</h4>"
                        f"<hr style='border:1px solid #333;margin:4px 0;'>",
                        unsafe_allow_html=True
                    )

                    html_items = ""
                    for item in items:
                        rhs = list(item.body)
                        rhs.insert(item.dot, "•")
                        rhs_str = " ".join(rhs)
                        lookaheads = ", ".join(sorted(item.lookahead))
                        html_items += (
                            f"<div style='font-family:Consolas,monospace;"
                            f"margin:2px 0;padding:2px 5px;"
                            f"background-color:#1a1a1a;border-radius:5px;'>"
                            f"<span style='color:#FFF;'>{item.head} → {rhs_str}</span> "
                            f"<span style='color:#00FFAA'>, {lookaheads}</span>"
                            f"</div>"
                        )

                    st.markdown(html_items + "</div>", unsafe_allow_html=True)

    with tabs[3]:
        if steps:
            st.dataframe(steps, use_container_width=True)
        else:
            st.info("No hay pasos para mostrar.")

    with tabs[4]:
        render_states(builder)

    with tabs[5]:
        st.header("🔹 Autómatas LR(1)")

        # --- AFN (items individuales con ε) ---
        st.subheader("1️⃣ AFN de items (no determinista)")
        afn_html = render_afn_items_lr1(builder)
        components.html(afn_html, height=600, scrolling=False)

        st.divider()

        # --- AFD (canónico LR(1)) ---
        st.subheader("2️⃣ AFD de estados canónicos (determinista)")
        afd_html = render_automata_svg_interactivo(builder)
        components.html(afd_html, height=600, scrolling=False)

else:
    st.info("Ingrese la gramática y la cadena, luego presione Analizar.")
