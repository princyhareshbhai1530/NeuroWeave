"""NEUROWEAVE: verify tensor/metadata compatibility before combining participants."""
from pathlib import Path
import numpy as np

D = Path('data/processed')
OLD = (3, 4, 5, 6)
NEW = (7, 8, 9)


def find_old(p):
    candidates = [D/f'participant_{p}.npz', D/f'participant_{p}_prepared.npz']
    for f in candidates:
        if f.exists(): return f
    return None


def inspect(path):
    z=np.load(path,allow_pickle=True)
    X=z['X']; y=z['y']; s=z['sessions'].astype(str)
    return X.shape, sorted(np.unique(s).tolist()), len(y), sorted(np.unique(y).tolist())

print('='*72)
print('NEUROWEAVE PREPROCESSING COMPATIBILITY CHECK')
print('='*72)
issues=[]
reference=None
for p in OLD:
    f=find_old(p)
    if not f:
        print(f'P{p}: MISSING earlier prepared file')
        issues.append(f'P{p} earlier file missing')
        continue
    info=inspect(f); print(f'P{p}: {f.name} | shape={info[0]} | sessions={info[1]} | labels={info[3]}')
    if reference is None: reference=info
for p in NEW:
    f=D/f'participant_{p}_standardized.npz'
    if not f.exists():
        print(f'P{p}: MISSING {f.name}'); issues.append(f'P{p} standardized file missing'); continue
    info=inspect(f); print(f'P{p}: {f.name} | shape={info[0]} | sessions={info[1]} | labels={info[3]}')
    if info[0][1:] != (22,640): issues.append(f'P{p} tensor dimensions not 22x640')
    if info[1] != ['0','1','2','3','4','5']: issues.append(f'P{p} session set differs')

print('\nRESULT')
if issues:
    print('NOT READY TO COMBINE')
    for x in issues: print(' -',x)
else:
    print('STRUCTURAL CHECK PASSED: all located files have compatible tensor/session structure.')
    print('CAUTION: matching shape does NOT prove identical signal preprocessing.')
    print('Before final scientific aggregation, compare the preparation parameters/code used for P3-6 with P7-9.')
