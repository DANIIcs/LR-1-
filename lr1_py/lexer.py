from __future__ import annotations
import re
from typing import List

# Simple regex-based lexer for arithmetic-like expressions
# Produces tokens: id, '+', '*', '(', ')'

TOKEN_SPEC = [
    ('WS',      r'[ \t\r\n]+'),
    ('NUMBER',  r'\d+(?:\.\d+)?'),
    ('ID',      r'[A-Za-z_][A-Za-z0-9_]*'),
    ('PLUS',    r'\+'),
    ('TIMES',   r'\*'),
    ('LPAREN',  r'\('),
    ('RPAREN',  r'\)'),
]
TOKEN_RE = re.compile('|'.join(f'(?P<{name}>{pat})' for name, pat in TOKEN_SPEC))


def tokenize_expr(text: str) -> List[str]:
    tokens: List[str] = []
    pos = 0
    while pos < len(text):
        m = TOKEN_RE.match(text, pos)
        if not m:
            # Unknown character: try to treat as literal terminal
            ch = text[pos]
            if not ch.strip():
                pos += 1
                continue
            raise ValueError(f"Carácter no reconocido en la posición {pos}: {repr(ch)}")
        kind = m.lastgroup
        val = m.group()
        pos = m.end()
        if kind == 'WS':
            continue
        elif kind in ('NUMBER', 'ID'):
            # Map both to 'id' to match typical grammars
            tokens.append('id')
        elif kind == 'PLUS':
            tokens.append('+')
        elif kind == 'TIMES':
            tokens.append('*')
        elif kind == 'LPAREN':
            tokens.append('(')
        elif kind == 'RPAREN':
            tokens.append(')')
        else:
            tokens.append(val)
    return tokens


def tokens_from_space_separated(text: str) -> List[str]:
    return [t for t in text.strip().split() if t]
