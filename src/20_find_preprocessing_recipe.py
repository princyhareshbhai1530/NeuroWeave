"""NEUROWEAVE: find the exact earlier preprocessing recipe in project source files."""
from pathlib import Path

ROOT = Path('.')
EXTS = {'.py', '.md', '.txt', '.json', '.yaml', '.yml'}
TERMS = ('MotorImagery', 'resample', 'tmin', 'tmax', 'fmin', 'fmax', '640', 'participant_03_X', 'participant_{subject:02d}_X')
SKIP = {'.venv', 'venv', '.git', '__pycache__'}

print('='*72)
print('NEUROWEAVE FIND EXACT PREPROCESSING RECIPE')
print('='*72)
found = 0
for path in ROOT.rglob('*'):
    if not path.is_file() or path.suffix.lower() not in EXTS:
        continue
    if any(part.lower() in SKIP for part in path.parts):
        continue
    try:
        lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
    except Exception:
        continue
    hits=[]
    for i,line in enumerate(lines,1):
        if any(term.lower() in line.lower() for term in TERMS):
            hits.append((i,line.strip()))
    if hits:
        found += 1
        print(f'\nFILE: {path}')
        for i,line in hits[:40]:
            print(f'  {i}: {line}')

if not found:
    print('\nNo matching preprocessing source was found.')
print('\nNEXT: paste this complete output into Copilot.')
