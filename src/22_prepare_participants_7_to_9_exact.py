"""NEUROWEAVE: prepare participants 7-9 using the exact established preprocessing recipe."""
from pathlib import Path
import json
import numpy as np
from moabb.datasets import Kumar2024
from moabb.paradigms import MotorImagery

OUTPUT_DIR = Path('outputs')
PARTICIPANTS = (7, 8, 9)

paradigm = MotorImagery(
    fmin=8,
    fmax=30,
    tmin=0.0,
    tmax=5.0,
    resample=128,
)


def main():
    print('=' * 72)
    print('NEUROWEAVE EXACT PREPROCESSING: PARTICIPANTS 7 TO 9')
    print('=' * 72)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dataset = Kumar2024()

    for subject in PARTICIPANTS:
        print('\n' + '=' * 72)
        print(f'PREPARING PARTICIPANT {subject}')
        print('=' * 72)
        X, y, metadata = paradigm.get_data(dataset=dataset, subjects=[subject])
        sessions = metadata['session'].astype(str).to_numpy()

        print(f'X shape: {X.shape}')
        print(f'labels: {np.unique(y).tolist()}')
        print(f'sessions: {sorted(np.unique(sessions).tolist())}')

        if X.shape[1:] != (22, 640):
            raise ValueError(f'Unexpected shape for participant {subject}: {X.shape}; expected (*, 22, 640)')

        np.save(OUTPUT_DIR / f'participant_{subject:02d}_X.npy', X)
        np.save(OUTPUT_DIR / f'participant_{subject:02d}_y.npy', y)
        np.save(OUTPUT_DIR / f'participant_{subject:02d}_sessions.npy', sessions)

        readiness = {
            'participant': subject,
            'X_shape': list(X.shape),
            'labels': np.unique(y).tolist(),
            'sessions': sorted(np.unique(sessions).tolist()),
            'preprocessing': {'fmin': 8, 'fmax': 30, 'tmin': 0.0, 'tmax': 5.0, 'resample': 128},
        }
        (OUTPUT_DIR / f'participant_{subject:02d}_readiness.json').write_text(
            json.dumps(readiness, indent=2), encoding='utf-8'
        )
        print(f'Saved participant {subject} using established preprocessing.')

    print('\nDONE: participants 7-9 now use the same declared preprocessing parameters as the earlier NeuroWeave pipeline.')


if __name__ == '__main__':
    main()
