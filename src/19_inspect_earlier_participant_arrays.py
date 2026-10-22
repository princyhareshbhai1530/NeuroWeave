"""NEUROWEAVE: inspect earlier output arrays for participants 3-6."""
from pathlib import Path
import numpy as np

OUT = Path('outputs')
SUBJECTS = (3, 4, 5, 6)

print('=' * 72)
print('NEUROWEAVE INSPECT EARLIER PARTICIPANT ARRAYS')
print('=' * 72)

for s in SUBJECTS:
    xfile = OUT / f'participant_{s:02d}_X.npy'
    yfile = OUT / f'participant_{s:02d}_y.npy'
    print(f'\nPARTICIPANT {s}')
    if not xfile.exists() or not yfile.exists():
        print(f'  MISSING: {xfile} or {yfile}')
        continue
    X = np.load(xfile, mmap_mode='r')
    y = np.load(yfile, allow_pickle=True)
    print(f'  X file: {xfile}')
    print(f'  y file: {yfile}')
    print(f'  X shape: {X.shape}')
    print(f'  X dtype: {X.dtype}')
    print(f'  y shape: {y.shape}')
    print(f'  y dtype: {y.dtype}')
    print(f'  labels: {np.unique(y).tolist()}')
    print(f'  trials match: {X.shape[0] == len(y)}')

print('\nIMPORTANT: This script only inspects existing files. It does not change them.')
print('NEXT: paste the complete output into Copilot.')
