from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Iterable
import re

Symbol = str
Production = List[Symbol]
Productions = Dict[Symbol, List[Production]]


class Grammar:
    EPSILON: Symbol = "ε"
    END_MARKER: Symbol = "$"

    def __init__(self, start_symbol: Symbol, productions: Productions):
        self.start_symbol: Symbol = start_symbol
        self.productions: Productions = {A: [list(p) for p in rhss] for A, rhss in productions.items()}
        self.nonterminals: Set[Symbol] = set(self.productions.keys())
        self.terminals: Set[Symbol] = self._infer_terminals()

    def _infer_terminals(self) -> Set[Symbol]:
        terms: Set[Symbol] = set()
        for rhss in self.productions.values():
            for prod in rhss:
                for X in prod:
                    if X == self.EPSILON:
                        continue
                    if X not in self.productions:
                        terms.add(X)
        return terms

    def augmented(self) -> "Grammar":
        aug_start = self.start_symbol + "'"
        while aug_start in self.nonterminals or aug_start in self.terminals:
            aug_start += "'"
        prods: Productions = {A: [p[:] for p in rhss] for A, rhss in self.productions.items()}
        prods[aug_start] = [[self.start_symbol]]
        return Grammar(aug_start, prods)

    @staticmethod
    def _tok(rhs: str) -> List[Symbol]:
        tokens = re.findall(r"'[^']*'|\"[^\"]*\"|[^\s]+", rhs)
        out: List[Symbol] = []
        for t in tokens:
            if t.startswith("'") and t.endswith("'"):
                out.append(t[1:-1])
            elif t.startswith('"') and t.endswith('"'):
                out.append(t[1:-1])
            else:
                out.append(t)
        return out

    @classmethod
    def parse_bnf(cls, text: str) -> "Grammar":
        lines = [ln.strip() for ln in text.splitlines()]
        pairs = []
        nts: Set[Symbol] = set()
        for ln in lines:
            if not ln or ln.startswith('#'):
                continue
            if '->' not in ln:
                raise ValueError(f"Línea inválida, falta '->': {ln}")
            lhs, rhs = ln.split('->', 1)
            A = lhs.strip()
            nts.add(A)
            pairs.append((A, rhs.strip()))
        if not pairs:
            raise ValueError('Gramática vacía')
        start = pairs[0][0]
        prods: Productions = {A: [] for A in nts}
        for A, rhs in pairs:
            for alt in [a.strip() for a in rhs.split('|')]:
                toks = [cls.EPSILON if t in (cls.EPSILON, 'epsilon', 'EPSILON') else t for t in cls._tok(alt)]
                prods[A].append(toks)
        return Grammar(start, prods)

    def compute_first(self) -> Dict[Symbol, Set[Symbol]]:
        first: Dict[Symbol, Set[Symbol]] = {}
        for t in self.terminals:
            first[t] = {t}
        first[self.EPSILON] = {self.EPSILON}
        for A in self.nonterminals:
            first.setdefault(A, set())
        changed = True
        while changed:
            changed = False
            for A, rhss in self.productions.items():
                for prod in rhss:
                    before = len(first[A])
                    for sym in prod:
                        for x in first.setdefault(sym, {sym} if sym in self.terminals or sym == self.EPSILON else set()):
                            if x != self.EPSILON:
                                first[A].add(x)
                        if self.EPSILON in first.get(sym, set()):
                            continue
                        else:
                            break
                    else:
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
            sym_first = first.get(sym, {sym} if sym in self.terminals else set())
            result.update(x for x in sym_first if x != self.EPSILON)
            if self.EPSILON in sym_first:
                continue
            else:
                break
        else:
            result.add(self.EPSILON)
        return result

    def compute_follow(self) -> Dict[Symbol, Set[Symbol]]:
        first = self.compute_first()
        follow: Dict[Symbol, Set[Symbol]] = {A: set() for A in self.nonterminals}
        follow[self.start_symbol].add(self.END_MARKER)

        changed = True
        while changed:
            changed = False
            for A, rhss in self.productions.items():
                for prod in rhss:
                    for i, B in enumerate(prod):
                        if B in self.nonterminals:
                            beta = prod[i + 1:]
                            first_beta = self.first_of_sequence(beta, first)
                            before = len(follow[B])
                            follow[B].update(x for x in first_beta if x != self.EPSILON)
                            if not beta or self.EPSILON in first_beta:
                                follow[B].update(follow[A])
                            if len(follow[B]) > before:
                                changed = True
        return follow