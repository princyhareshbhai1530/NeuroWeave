"""NEUROWEAVE: locate earlier participant 3-6 arrays before regenerating anything."""
from pathlib import Path

ROOT = Path('.')
SUBJECTS = (3, 4, 5, 6)
EXTS = {'.npz', '.npy', '.pkl', '.pickle'}
SKIP_PARTS = {'.venv', 'venv', '__pycache__', '.git'}

print('=' * 72)
print('NEUROWEAVE LOCATE EARLIER PARTICIPANT FILES')
print('=' * 72)

files = []
for p in ROOT.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in EXTS:
        continue
    if any(part.lower() in SKIP_PARTS for part in p.parts):
        continue
    files.append(p)

for subject in SUBJECTS:
    tokens = [f'participant_{subject}', f'participant{subject}', f'subject_{subject}', f'subject{subject}', f'p{subject}']
    matches = [p for p in files if any(t in p.name.lower() for t in tokens)]
    print(f'\nPARTICIPANT {subject}')
    if matches:
        for p in matches:
            print(f'  FOUND: {p}')
    else:
        print('  No obvious participant-specific array file found.')

print('\nOther candidate data files:')
for p in files:
    print(f'  {p}')

print('\nNEXT: paste this complete output back into Copilot.')
print('Do not regenerate participants 3-6 yet; first determine where the prior analysis loaded them from.')
