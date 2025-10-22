from __future__ import annotations
from typing import Dict, List, Tuple, Any

from .grammar import Grammar, Symbol

ActionValue = Tuple[str, int] | Tuple[str, Tuple[str, List[str]]] | Tuple[str]


class LR1Parser:
    def __init__(self, grammar: Grammar, action: Dict[Tuple[int, Symbol], ActionValue], goto: Dict[Tuple[int, Symbol], int]):
        self.grammar = grammar
        self.action = action
        self.goto = goto

    def parse(self, tokens: List[Symbol]) -> dict:
        # Ensure end marker
        if not tokens or tokens[-1] != Grammar.END_MARKER:
            tokens = tokens + [Grammar.END_MARKER]
        state_stack: List[int] = [0]
        sym_stack: List[Symbol] = []
        pos = 0
        steps: List[dict] = []
        reductions: List[tuple[str, List[str]]] = []

        def snapshot(action_desc: str):
            steps.append({
                'states': state_stack.copy(),
                'symbols': sym_stack.copy(),
                'input': tokens[pos:],
                'action': action_desc,
            })

        snapshot('init')
        while True:
            s = state_stack[-1]
            a = tokens[pos]
            act = self.action.get((s, a))
            if act is None:
                snapshot(f'error: no ACTION[{s}, {a}]')
                return {
                    'accepted': False,
                    'error': f'No hay acción para estado {s} y símbolo {a}',
                    'steps': steps,
                }
            if act[0] == 's':
                j = act[1]  # type: ignore[index]
                sym_stack.append(a)
                state_stack.append(j)  # shift
                pos += 1
                snapshot(f'shift {a}, goto state {j}')
            elif act[0] == 'r':
                head, body = act[1]  # type: ignore[index]
                k = len(body)
                if body == [Grammar.EPSILON]:
                    k = 0
                # pop k
                for _ in range(k):
                    if sym_stack:
                        sym_stack.pop()
                    if state_stack:
                        state_stack.pop()
                reductions.append((head, body))
                t = state_stack[-1]
                sym_stack.append(head)
                g = self.goto.get((t, head))
                if g is None:
                    snapshot(f'error: no GOTO[{t}, {head}]')
                    return {
                        'accepted': False,
                        'error': f'No hay transición GOTO para ({t}, {head})',
                        'steps': steps,
                        'reductions': reductions,
                    }
                state_stack.append(g)
                snapshot(f'reduce {head} -> {" ".join(body) if body else Grammar.EPSILON}, goto {g}')
            elif act[0] == 'acc':
                snapshot('accept')
                return {
                    'accepted': True,
                    'steps': steps,
                    'reductions': reductions,
                }
            else:
                snapshot(f'error: acción desconocida {act}')
                return {
                    'accepted': False,
                    'error': f'Acción desconocida: {act}',
                    'steps': steps,
                    'reductions': reductions,
                }
