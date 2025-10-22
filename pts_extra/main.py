from __future__ import annotations
import sys
import os

from .scanner import Scanner, ejecutar_scanner
from .parser_lr1 import build_parser
from .lexer import tokenize_expr

HELP = """
Uso: python -m pts_extra.main <ruta_input> [ruta_gramatica]
- ruta_input: archivo de texto con la cadena a analizar (una línea o varias)
- ruta_gramatica (opcional): archivo con gramática en BNF simple
Si no se proporciona gramática, se usa la de expresiones por defecto.
"""

def main(argv: list[str] | None = None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 1:
        print(HELP)
        return 1

    input_path = argv[0]
    grammar_path = argv[1] if len(argv) >= 2 else None

    if not os.path.isfile(input_path):
        print(f"No se encontró el archivo: {input_path}")
        return 1

    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()

    grammar_text = None
    if grammar_path:
        if not os.path.isfile(grammar_path):
            print(f"No se encontró gramática: {grammar_path}")
            return 1
        grammar_text = open(grammar_path, 'r', encoding='utf-8').read()
    else:
        # Buscar un grammar.txt local por conveniencia
        default_grammar = os.path.join(os.path.dirname(__file__), 'grammar.txt')
        if os.path.isfile(default_grammar):
            grammar_text = open(default_grammar, 'r', encoding='utf-8').read()

    # Scanner: genera inputs/<name>_tokens.txt
    scanner = Scanner(text)
    ejecutar_scanner(scanner, input_path)

    # Parser LR(1)
    builder, parser = build_parser(grammar_text)
    tokens = tokenize_expr(text)
    parsed = parser.parse(tokens)

    print("=== RESULTADOS LR(1) ===")
    print(f"Estados: {len(builder.states)}")
    if builder.conflicts:
        print("Conflictos:")
        for c in builder.conflicts:
            print(" -", c)
    print("Aceptado:" , parsed.get('accepted'))
    if not parsed.get('accepted') and 'error' in parsed:
        print("Error:", parsed['error'])

    # Derivación aproximada
    if parsed.get('reductions'):
        print("\nDerivación (aprox.):")
        from webapp.app import derive_sentential_forms
        deriv = derive_sentential_forms(builder.aug.start_symbol, parsed['reductions'])
        for i, sent in enumerate(deriv):
            print(f"{i}:", ' '.join(sent))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
