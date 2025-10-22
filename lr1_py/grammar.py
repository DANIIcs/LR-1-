from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Iterable
import re

Symbol = str
Production = List[Symbol]
Productions = Dict[Symbol, List[Production]]


class Grammar:
    """
    Simple context-free grammar representation with FIRST set computation
    and a small BNF-like parser.

    Notation:
    - Each rule in text: A -> α | β | ...
    - Tokens separated by spaces. Terminals can be written as quoted strings like '+' or 'id'.
    - Epsilon can be: ε or epsilon
    - Lines starting with # are comments. Empty lines ignored.
    """

    EPSILON: Symbol = "ε"
    END_MARKER: Symbol = "$"

    def __init__(self, start_symbol: Symbol, productions: Productions):
        self.start_symbol: Symbol = start_symbol
        # Normalize productions to lists of lists (no tuples)
        self.productions: Productions = {
            A: [list(prod) for prod in rhs]
            for A, rhs in productions.items()
        }
        self.nonterminals: Set[Symbol] = set(self.productions.keys())
        self.terminals: Set[Symbol] = self._infer_terminals()

    def _infer_terminals(self) -> Set[Symbol]:
        terms: Set[Symbol] = set()
        for A, rhss in self.productions.items():
            for prod in rhss:
                for X in prod:
                    if X == self.EPSILON:
                        continue
                    if X not in self.productions:  # not a nonterminal
                        terms.add(X)
        # Conventionally, add end marker but it's not a grammar terminal
        return terms

    def augmented(self) -> "Grammar":
        """Return an augmented grammar S' -> S where S is the current start symbol."""
        aug_start = self.start_symbol + "'"
        while aug_start in self.nonterminals or aug_start in self.terminals:
            aug_start += "'"
        prods: Productions = {A: [p[:] for p in rhss] for A, rhss in self.productions.items()}
        prods[aug_start] = [[self.start_symbol]]
        return Grammar(aug_start, prods)

    @staticmethod
    def _tokenize_rhs(rhs: str) -> List[Symbol]:
        # Split by spaces but keep quoted tokens intact
        # Matches single-quoted, double-quoted or bare tokens
        tokens = re.findall(r"'[^']*'|\"[^\"]*\"|[^\s]+", rhs)
        cleaned: List[Symbol] = []
        for t in tokens:
            if t.startswith("'") and t.endswith("'"):
                cleaned.append(t[1:-1])
            elif t.startswith('"') and t.endswith('"'):
                cleaned.append(t[1:-1])
            else:
                cleaned.append(t)
        return cleaned

    @classmethod
    def parse_bnf(cls, text: str) -> "Grammar":
        lines = [ln.strip() for ln in text.splitlines()]
        # First pass: collect LHS nonterminals
        lhs_list: List[Tuple[Symbol, str]] = []
        nonterms: Set[Symbol] = set()
        for ln in lines:
            if not ln or ln.startswith('#'):
                continue
            if '->' not in ln:
                raise ValueError(f"Línea inválida, falta '->': {ln}")
            lhs, rhs = ln.split('->', 1)
            A = lhs.strip()
            rhs_raw = rhs.strip()
            if not A:
                raise ValueError(f"No-terminal vacío en: {ln}")
            lhs_list.append((A, rhs_raw))
            nonterms.add(A)
        if not lhs_list:
            raise ValueError("No se encontraron producciones en la gramática")
        start = lhs_list[0][0]
        productions: Productions = {A: [] for A in nonterms}
        for A, rhs_raw in lhs_list:
            alts = [alt.strip() for alt in rhs_raw.split('|')]
            for alt in alts:
                if not alt:
                    raise ValueError(f"Producción vacía en {A} -> |")
                tokens = cls._tokenize_rhs(alt)
                prod: Production = []
                for tok in tokens:
                    if tok in ("epsilon", "EPSILON", "EPS", "empty", cls.EPSILON):
                        prod.append(cls.EPSILON)
                    else:
                        prod.append(tok)
                productions[A].append(prod)
        return Grammar(start, productions)

    # FIRST set computation
    def compute_first(self) -> Dict[Symbol, Set[Symbol]]:
        first: Dict[Symbol, Set[Symbol]] = {}
        # Terminals and epsilon
        for t in self.terminals:
            first[t] = {t}
        first[self.EPSILON] = {self.EPSILON}
        # Nonterminals initialize empty
        for A in self.nonterminals:
            first.setdefault(A, set())
        changed = True
        while changed:
            changed = False
            for A, rhss in self.productions.items():
                for prod in rhss:
                    before = len(first[A])
                    for sym in prod:
                        # Merge FIRST(sym) \ {ε}
                        for x in first.setdefault(sym, {sym} if sym in self.terminals or sym == self.EPSILON else set()):
                            if x != self.EPSILON:
                                first[A].add(x)
                        # If ε in FIRST(sym) continue to next sym, else stop
                        if self.EPSILON in first.get(sym, set()):
                            continue
                        else:
                            break
                    else:
                        # All could derive ε
                        first[A].add(self.EPSILON)
                    if len(first[A]) > before:
                        changed = True
        return first

    def first_of_sequence(self, seq: Iterable[Symbol], first: Dict[Symbol, Set[Symbol]] | None = None) -> Set[Symbol]:
        if first is None:
            first = self.compute_first()
        result: Set[Symbol] = set()
        seq_list = list(seq)
        if not seq_list:
            result.add(self.EPSILON)
            return result
        for sym in seq_list:
            sym_first = first.get(sym)
            if sym_first is None:
                # Unknown symbol, treat as terminal itself
                sym_first = {sym}
            result.update(x for x in sym_first if x != self.EPSILON)
            if self.EPSILON in sym_first:
                continue
            else:
                break
        else:
            result.add(self.EPSILON)
        return result

    def __str__(self) -> str:
        lines: List[str] = []
        for A, rhss in self.productions.items():
            rhs_str = " | ".join(" ".join(prod) for prod in rhss)
            lines.append(f"{A} -> {rhs_str}")
        return "\n".join(lines)
