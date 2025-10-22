from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .grammar import Grammar
from .lr1 import LR1Builder
from .parser import LR1Parser
from .lexer import tokenize_expr, tokens_from_space_separated

EXPR_GRAMMAR = """
# Gramática de expresiones aritméticas (LR(1))
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
""".strip()


class LR1App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LR(1) Parser - Proyecto")
        self.geometry("1100x700")
        self._builder: Optional[LR1Builder] = None
        self._parser: Optional[LR1Parser] = None
        self._grammar: Optional[Grammar] = None
        self._tokenization_mode = tk.StringVar(value='lex')  # 'lex' or 'spaces'

        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Top: Grammar + Controls
        top = ttk.Frame(container)
        top.pack(fill=tk.BOTH, expand=True)

        # Grammar text
        left = ttk.Frame(top)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(left, text="Gramática (BNF)").pack(anchor='w')
        self.txt_grammar = tk.Text(left, height=20, wrap=tk.NONE)
        self.txt_grammar.pack(fill=tk.BOTH, expand=True)
        self.txt_grammar.insert('1.0', EXPR_GRAMMAR)
        # Scrollbars for grammar
        yscroll = ttk.Scrollbar(left, orient='vertical', command=self.txt_grammar.yview)
        xscroll = ttk.Scrollbar(left, orient='horizontal', command=self.txt_grammar.xview)
        self.txt_grammar.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)

        # Controls and input
        right = ttk.Frame(top)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8,0))
        ttk.Label(right, text="Cadena de entrada").pack(anchor='w')
        self.txt_input = tk.Text(right, height=4)
        self.txt_input.pack(fill=tk.X)
        self.txt_input.insert('1.0', 'id + id * id')

        mode_frame = ttk.LabelFrame(right, text='Tokenización')
        mode_frame.pack(fill=tk.X, pady=4)
        ttk.Radiobutton(mode_frame, text='Léxico (id,+,*,(,))', value='lex', variable=self._tokenization_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text='Separada por espacios', value='spaces', variable=self._tokenization_mode).pack(side=tk.LEFT)

        btns = ttk.Frame(right)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text='Cargar ejemplo', command=self.load_example).pack(side=tk.LEFT)
        ttk.Button(btns, text='Construir parser', command=self.build_parser).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text='Analizar', command=self.run_parse).pack(side=tk.LEFT)

        # Bottom: Output areas
        bottom = ttk.Panedwindow(container, orient=tk.HORIZONTAL)
        bottom.pack(fill=tk.BOTH, expand=True, pady=(8,0))

        frame_tables = ttk.Labelframe(bottom, text='Resumen / Tablas')
        self.txt_tables = tk.Text(frame_tables, wrap=tk.NONE)
        y1 = ttk.Scrollbar(frame_tables, orient='vertical', command=self.txt_tables.yview)
        x1 = ttk.Scrollbar(frame_tables, orient='horizontal', command=self.txt_tables.xview)
        self.txt_tables.configure(yscrollcommand=y1.set, xscrollcommand=x1.set)
        self.txt_tables.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y1.pack(side=tk.RIGHT, fill=tk.Y)
        x1.pack(side=tk.BOTTOM, fill=tk.X)

        frame_steps = ttk.Labelframe(bottom, text='Ejecución del parser')
        self.txt_steps = tk.Text(frame_steps, wrap=tk.NONE)
        y2 = ttk.Scrollbar(frame_steps, orient='vertical', command=self.txt_steps.yview)
        x2 = ttk.Scrollbar(frame_steps, orient='horizontal', command=self.txt_steps.xview)
        self.txt_steps.configure(yscrollcommand=y2.set, xscrollcommand=x2.set)
        self.txt_steps.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y2.pack(side=tk.RIGHT, fill=tk.Y)
        x2.pack(side=tk.BOTTOM, fill=tk.X)

        bottom.add(frame_tables, weight=1)
        bottom.add(frame_steps, weight=1)

    def load_example(self):
        self.txt_grammar.delete('1.0', tk.END)
        self.txt_grammar.insert('1.0', EXPR_GRAMMAR)
        self.txt_input.delete('1.0', tk.END)
        self.txt_input.insert('1.0', 'id + id * id')
        self._tokenization_mode.set('lex')

    def build_parser(self):
        grammar_text = self.txt_grammar.get('1.0', tk.END).strip()
        if not grammar_text:
            messagebox.showwarning('Aviso', 'Proporciona la gramática')
            return
        try:
            g = Grammar.parse_bnf(grammar_text)
            builder = LR1Builder(g)
            builder.build_tables()
            self._grammar = g
            self._builder = builder
            self._parser = LR1Parser(builder.aug, builder.action, builder.goto_table)
        except Exception as e:
            messagebox.showerror('Error al construir', str(e))
            return
        self.show_tables()

    def show_tables(self):
        if not self._builder:
            return
        b = self._builder
        txt = []
        txt.append(f"Estados: {len(b.states)}")
        if b.conflicts:
            txt.append('\nConflictos:')
            for c in b.conflicts:
                txt.append('  - ' + c)
        txt.append('\nACTION:')
        for (s, a), v in sorted(b.action.items()):
            txt.append(f"  ({s}, {a}) -> {v}")
        txt.append('\nGOTO:')
        for (s, A), j in sorted(b.goto_table.items()):
            txt.append(f"  ({s}, {A}) -> {j}")
        self.txt_tables.delete('1.0', tk.END)
        self.txt_tables.insert('1.0', '\n'.join(txt))

    def run_parse(self):
        if not self._parser:
            self.build_parser()
            if not self._parser:
                return
        input_text = self.txt_input.get('1.0', tk.END).strip()
        mode = self._tokenization_mode.get()
        try:
            if mode == 'lex':
                tokens = tokenize_expr(input_text)
            else:
                tokens = tokens_from_space_separated(input_text)
        except Exception as e:
            messagebox.showerror('Error de entrada', str(e))
            return
        result = self._parser.parse(tokens)
        out = []
        for i, st in enumerate(result['steps']):
            out.append(f"Paso {i}:\n  Estados: {st['states']}\n  Símbolos: {st['symbols']}\n  Entrada: {' '.join(st['input'])}\n  Acción: {st['action']}\n")
        out.append('\nResultado: ' + ('ACEPTADO' if result.get('accepted') else 'RECHAZADO'))
        if not result.get('accepted') and 'error' in result:
            out.append('Error: ' + result['error'])
        self.txt_steps.delete('1.0', tk.END)
        self.txt_steps.insert('1.0', '\n'.join(out))


def main():
    app = LR1App()
    app.mainloop()


if __name__ == '__main__':
    main()
