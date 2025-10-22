from __future__ import annotations
from typing import List
from .core.lexer import tokenize_expr
from .token import Token

class Scanner:
    def __init__(self, src: str):
        self.src = src
        self.tokens: List[Token] = [Token('SYM', t) for t in tokenize_expr(src)]
        self.pos = 0

    def nextToken(self) -> Token:
        if self.pos >= len(self.tokens):
            return Token('END', '')
        t = self.tokens[self.pos]
        self.pos += 1
        return t


def ejecutar_scanner(scanner: Scanner, input_file: str):
    # Escribe archivo inputs/<name>_tokens.txt como en C++
    import os
    base = os.path.basename(input_file)
    name, _ = os.path.splitext(base)
    out_path = os.path.join(os.path.dirname(input_file), f"{name}_tokens.txt")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('Scanner\n\n')
        while True:
            tok = scanner.nextToken()
            f.write(str(tok) + '\n')
            if tok.type == 'END':
                f.write('\nScanner exitoso\n\n')
                break
