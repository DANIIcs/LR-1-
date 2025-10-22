from flask import Flask, render_template, request, jsonify
import sys
import os

# Add the parent directory to Python path so we can import pts_extra
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pts_extra.grammar import Grammar
from pts_extra.lr1 import LR1Builder
from pts_extra.parser import LR1Parser

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def analyze():
    grammar_text = request.form.get('grammar', '').strip()
    input_string = request.form.get('string', '').strip()
    
    if not grammar_text or not input_string:
        return render_template('index.html', result={
            'success': False,
            'error': 'Por favor proporciona tanto la gramática como la cadena de entrada.'
        })
    
    try:
        # Parse grammar
        grammar = Grammar.parse_bnf(grammar_text)
        
        # Build LR(1) tables
        builder = LR1Builder(grammar)
        builder.build_tables()
        
        # Check for conflicts
        if builder.conflicts:
            return render_template('index.html', result={
                'success': False,
                'error': 'La gramática tiene conflictos y no es LR(1)',
                'conflicts': [str(conflict) for conflict in builder.conflicts]
            })
        
        # Parse the input string
        parser = LR1Parser(grammar, builder.action, builder.goto_table)
        
        # Tokenize input (simple space separation for now)
        tokens = input_string.split()
        
        try:
            result_data = parser.parse(tokens)
            
            if result_data.get('accepted'):
                # Build derivation from reductions (reverse order)
                derivation = build_derivation(result_data.get('reductions', []), grammar)
                
                # Collect data for the template
                result = {
                    'success': True,
                    'derivation': derivation,
                    'parse_steps': format_parse_steps(result_data.get('steps', [])),
                    'states': format_states(builder.states),
                    'action_table': format_action_table(builder),
                    'goto_table': format_goto_table(builder),
                    'terminals': sorted(list(grammar.terminals | {Grammar.END_MARKER})),
                    'nonterminals': sorted(list(grammar.nonterminals)),
                    'productions_count': len(grammar.productions)
                }
                
                return render_template('index.html', result=result)
            else:
                return render_template('index.html', result={
                    'success': False,
                    'error': result_data.get('error', 'La cadena no es aceptada por la gramática')
                })
                
        except Exception as e:
            return render_template('index.html', result={
                'success': False,
                'error': f'Error durante el análisis: {str(e)}'
            })
            
    except Exception as e:
        return render_template('index.html', result={
            'success': False,
            'error': f'Error al procesar la gramática: {str(e)}'
        })

def build_derivation(reductions, grammar):
    """Build derivation sequence from reductions"""
    if not reductions:
        return []
    
    derivation = []
    # Start with the start symbol
    current = grammar.start_symbol
    derivation.append(current)
    
    # Apply reductions in reverse order to get leftmost derivation
    for head, body in reversed(reductions):
        if body == [Grammar.EPSILON]:
            body_str = Grammar.EPSILON
        else:
            body_str = ' '.join(body)
        derivation.append(f"{head} → {body_str}")
    
    return derivation

def format_parse_steps(steps):
    """Format parse steps for display"""
    formatted_steps = []
    for step in steps:
        # Handle both old and new step formats
        if 'stack' in step:
            stack = step['stack']
            input_tokens = step['input']
        else:
            # New format with 'states' and 'symbols'
            stack = step.get('symbols', [])
            input_tokens = step.get('input', [])
            
        formatted_steps.append({
            'stack': ' '.join(str(x) for x in stack),
            'input': ' '.join(str(x) for x in input_tokens),
            'action': step.get('action', '')
        })
    return formatted_steps

def format_states(states):
    """Format LR(1) states for display"""
    formatted_states = []
    for state_id, state in enumerate(states):
        items = []
        for item in state:  # state is a set of LR1Item objects
            # Format the item nicely
            # Insert the dot at the right position
            rhs = list(item.body)
            rhs.insert(item.dot, '•')
            
            production_str = f"{item.head} -> {' '.join(rhs)}"
            items.append({
                'production': production_str,
                'lookahead': item.lookahead
            })
        
        formatted_states.append({
            'id': state_id,
            'items': items
        })
    
    return formatted_states

def format_action_table(builder):
    """Format ACTION table for display"""
    terminals = sorted(list(builder.aug.terminals | {Grammar.END_MARKER}))
    action_table = []
    
    for state_id in range(len(builder.states)):
        row = {}
        for terminal in terminals:
            key = (state_id, terminal)
            if key in builder.action:
                action = builder.action[key]
                if action[0] == 's':
                    row[terminal] = f"s{action[1]}"
                elif action[0] == 'r':
                    # action[1] is (head, body) tuple
                    head, body = action[1]
                    # Find production index for display
                    prod_idx = 0
                    # Search through all productions to find matching one
                    for lhs, rhss in builder.aug.productions.items():
                        for rhs in rhss:
                            if lhs == head and rhs == body:
                                break
                            prod_idx += 1
                        else:
                            continue
                        break
                    row[terminal] = f"r{prod_idx}"
                elif action[0] == 'acc':
                    row[terminal] = "accept"
        action_table.append(row)
    
    return action_table

def format_goto_table(builder):
    """Format GOTO table for display"""
    nonterminals = sorted(list(builder.aug.nonterminals))
    goto_table = []
    
    for state_id in range(len(builder.states)):
        row = {}
        for nonterminal in nonterminals:
            key = (state_id, nonterminal)
            if key in builder.goto_table:
                next_state = builder.goto_table[key]
                row[nonterminal] = str(next_state)
        goto_table.append(row)
    
    return goto_table

if __name__ == '__main__':
    app.run(debug=True, port=5000)