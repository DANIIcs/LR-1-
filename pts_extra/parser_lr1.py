from __future__ import annotations
from typing import List, Dict, Tuple

from .grammar import Grammar
from .lr1 import LR1Builder
from .parser import LR1Parser

EXPR_GRAMMAR = """
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
""".strip()


def build_parser(grammar_text: str | None = None):
    g = Grammar.parse_bnf(grammar_text.strip() if grammar_text else EXPR_GRAMMAR)
    b = LR1Builder(g)
    b.build_tables()
    p = LR1Parser(b.aug, b.action, b.goto_table)
    return b, p


def parse_string(s: str, grammar_text: str | None = None) -> dict:
    b, p = build_parser(grammar_text)
    from .lexer import tokenize_expr
    tokens = tokenize_expr(s)
    return {'builder': b, 'result': p.parse(tokens)}
