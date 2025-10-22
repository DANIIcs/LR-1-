import unittest

from lr1_py.grammar import Grammar
from lr1_py.lr1 import LR1Builder
from lr1_py.parser import LR1Parser
from lr1_py.lexer import tokenize_expr

EXPR = """
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
""".strip()


class TestLR1Basic(unittest.TestCase):
    def test_build_and_parse(self):
        g = Grammar.parse_bnf(EXPR)
        b = LR1Builder(g)
        b.build_tables()
        self.assertGreater(len(b.states), 0)
        self.assertEqual([], b.conflicts)
        p = LR1Parser(b.aug, b.action, b.goto_table)
        tokens = tokenize_expr("id + id * id")
        result = p.parse(tokens)
        self.assertTrue(result['accepted'])


if __name__ == '__main__':
    unittest.main()
