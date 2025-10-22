import os
import subprocess
import sys

ROOT = os.path.dirname(__file__)
INPUT_DIR = os.path.join(ROOT, 'inputs')
OUTPUT_DIR = os.path.join(ROOT, 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

python = os.path.join(os.path.dirname(ROOT), '.venv', 'Scripts', 'python.exe')
if not os.path.isfile(python):
    python = sys.executable

for i in range(1, 6):
    name = f'input{i}.txt'
    path = os.path.join(INPUT_DIR, name)
    if not os.path.isfile(path):
        print(f'{name} no encontrado en inputs/')
        continue
    print('Ejecutando', name)
    cmd = [python, '-m', 'pts_extra.main', path]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(ROOT))

    with open(os.path.join(OUTPUT_DIR, f'output{i}.txt'), 'w', encoding='utf-8') as f:
        f.write('=== STDOUT ===\n')
        f.write(result.stdout)
        f.write('\n=== STDERR ===\n')
        f.write(result.stderr)

    base, _ = os.path.splitext(name)
    tokens_in = os.path.join(INPUT_DIR, f'{base}_tokens.txt')
    if os.path.isfile(tokens_in):
        os.replace(tokens_in, os.path.join(OUTPUT_DIR, f'tokens_{i}.txt'))
