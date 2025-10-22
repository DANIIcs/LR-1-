from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Iterable, Optional

from .grammar import Grammar, Symbol


@dataclass(frozen=True)
class LR1Item:
    head: Symbol
    body: Tuple[Symbol, ...]
    dot: int
    lookahead: Symbol

    def next_symbol(self) -> Optional[Symbol]:
        if self.dot < len(self.body):
            return self.body[self.dot]
        return None

    def at_end(self) -> bool:
        return self.dot >= len(self.body)

    def advance(self) -> "LR1Item":
        return LR1Item(self.head, self.body, self.dot + 1, self.lookahead)

    def __str__(self) -> str:
        before = " ".join(self.body[: self.dot])
        after = " ".join(self.body[self.dot :])
        return f"[{self.head} -> {before} • {after}, {self.lookahead}]"


class LR1Builder:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.aug = grammar.augmented()
        self.first = self.aug.compute_first()
        self.states: List[Set[LR1Item]] = []
        self.transitions: Dict[Tuple[int, Symbol], int] = {}
        self.action: Dict[Tuple[int, Symbol], Tuple] = {}
        self.goto_table: Dict[Tuple[int, Symbol], int] = {}
        self.conflicts: List[str] = []

    def closure(self, items: Iterable[LR1Item]) -> Set[LR1Item]:
        I: Set[LR1Item] = set(items)
        changed = True
        while changed:
            changed = False
            new_items: Set[LR1Item] = set()
            for it in list(I):
                X = it.next_symbol()
                if X and X in self.aug.nonterminals:
                    beta = list(it.body[it.dot + 1 :])
                    lookaheads = self.aug.first_of_sequence(beta, self.first)
                    if Grammar.EPSILON in lookaheads:
                        lookaheads = (lookaheads - {Grammar.EPSILON}) | {it.lookahead}
                    for prod in self.aug.productions[X]:
                        prod_list = prod if prod != [Grammar.EPSILON] else []
                        for a in lookaheads:
                            new_items.add(LR1Item(X, tuple(prod_list), 0, a))
            for ni in new_items:
                if ni not in I:
                    I.add(ni)
                    changed = True
        return I

    def goto_set(self, I: Set[LR1Item], X: Symbol) -> Set[LR1Item]:
        advanced = [it.advance() for it in I if it.next_symbol() == X]
        if not advanced:
            return set()
        return self.closure(advanced)

    def build_canonical_collection(self):
        start_item = LR1Item(self.aug.start_symbol, (self.aug.productions[self.aug.start_symbol][0][0],), 0, Grammar.END_MARKER)
        I0 = self.closure([start_item])
        C: List[Set[LR1Item]] = []
        C.append(I0)
        state_index: Dict[frozenset[LR1Item], int] = {frozenset(I0): 0}
        self.states = C
        worklist = [0]
        symbols = list(self.aug.terminals | self.aug.nonterminals)
        while worklist:
            i = worklist.pop()
            I = self.states[i]
            for X in symbols:
                goto_set = self.goto_set(I, X)
                if not goto_set:
                    continue
                fr = frozenset(goto_set)
                if fr not in state_index:
                    j = len(self.states)
                    state_index[fr] = j
                    self.states.append(goto_set)
                    worklist.append(j)
                else:
                    j = state_index[fr]
                self.transitions[(i, X)] = j

    def build_tables(self):
        self.build_canonical_collection()
        self.action = {}
        self.goto_table = {}
        self.conflicts = []
        for i, I in enumerate(self.states):
            for it in I:
                a = it.next_symbol()
                if a and a in self.aug.terminals:
                    j = self.transitions.get((i, a))
                    if j is not None:
                        self._set_action(i, a, ('s', j))
            for it in I:
                if it.at_end():
                    if it.head == self.aug.start_symbol and it.lookahead == Grammar.END_MARKER:
                        self._set_action(i, Grammar.END_MARKER, ('acc',))
                    else:
                        prod = list(it.body)
                        self._set_action(i, it.lookahead, ('r', (it.head, prod)))
            for A in self.aug.nonterminals:
                j = self.transitions.get((i, A))
                if j is not None:
                    self.goto_table[(i, A)] = j

    def _set_action(self, state: int, terminal: Symbol, value: Tuple):
        key = (state, terminal)
        existing = self.action.get(key)
        if existing and existing != value:
            self.conflicts.append(f"Conflicto en estado {state}, terminal '{terminal}': {existing} vs {value}")
        else:
            self.action[key] = value

    def summary(self) -> str:
        lines: List[str] = []
        lines.append(f"Estados: {len(self.states)}")
        for i, I in enumerate(self.states):
            lines.append(f"\nEstado {i}:")
            for it in sorted(I, key=lambda x: (x.head, x.body, x.dot, x.lookahead)):
                lines.append(f"  {it}")
        lines.append("\nACTION:")
        for (s, a), v in sorted(self.action.items()):
            lines.append(f"  ({s}, {a}) -> {v}")
        lines.append("\nGOTO:")
        for (s, A), j in sorted(self.goto_table.items()):
            lines.append(f"  ({s}, {A}) -> {j}")
        if self.conflicts:
            lines.append("\nConflictos:")
            for c in self.conflicts:
                lines.append(f"  - {c}")
        return "\n".join(lines)
