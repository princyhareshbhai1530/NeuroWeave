"""NEUROWEAVE: search only project code/docs for the original EEG preprocessing recipe."""
from pathlib import Path

ROOT = Path('.')
SEARCH_DIRS = [Path('src'), Path('outputs'), Path('results'), Path('docs')]
ROOT_FILES = [p for p in ROOT.iterdir() if p.is_file()] if ROOT.exists() else []
EXTS = {'.py', '.md', '.txt', '.json', '.yaml', '.yml'}
TERMS = ('MotorImagery', 'resample=', 'resample =', 'tmin=', 'tmax=', 'fmin=', 'fmax=',
         'participant_03_X', 'participant_{subject:02d}_X', 'np.save', '640')

candidates = list(ROOT_FILES)
for d in SEARCH_DIRS:
    if d.exists():
        candidates.extend(p for p in d.rglob('*') if p.is_file())

seen=set(); hits_total=0
print('='*72)
print('NEUROWEAVE PROJECT-ONLY PREPROCESSING SEARCH')
print('='*72)
for path in candidates:
    try:
        rp=path.resolve()
        if rp in seen or path.suffix.lower() not in EXTS:
            continue
        seen.add(rp)
        lines=path.read_text(encoding='utf-8', errors='ignore').splitlines()
    except Exception:
        continue
    hits=[]
    for i,line in enumerate(lines,1):
        if any(t.lower() in line.lower() for t in TERMS):
            hits.append((i,line.strip()))
    if hits:
        hits_total += len(hits)
        print(f'\nFILE: {path}')
        for i,line in hits[:80]:
            print(f'  {i}: {line}')

if hits_total == 0:
    print('\nNo preprocessing recipe found in project code/docs.')
print('\nNOTE: data_cache is intentionally excluded because numeric race logs caused false matches.')
print('NEXT: paste the complete output into Copilot.')
