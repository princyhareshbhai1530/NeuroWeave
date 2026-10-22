"""NEUROWEAVE: analyze participants 7-9 using exactly preprocessed output arrays."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from pyriemann.estimation import Covariances
from pyriemann.tangentspace import TangentSpace
from pyriemann.utils.distance import distance_riemann
from pyriemann.utils.mean import mean_riemann

OUTPUT_DIR = Path('outputs')
RESULTS_DIR = Path('results')
PARTICIPANTS = (7, 8, 9)


def decoder():
    return make_pipeline(
        Covariances(estimator='oas'),
        TangentSpace(metric='riemann'),
        LinearDiscriminantAnalysis(solver='lsqr', shrinkage='auto'),
    )


def metrics(model, X, y):
    pred = model.predict(X)
    bal = balanced_accuracy_score(y, pred)
    f1 = f1_score(y, pred, average='weighted')
    try:
        classes = list(model.classes_)
        positive_index = classes.index('right_hand') if 'right_hand' in classes else 1
        prob = model.predict_proba(X)[:, positive_index]
        binary_y = (y == classes[positive_index]).astype(int)
        auc = roc_auc_score(binary_y, prob)
    except Exception:
        auc = np.nan
    return bal, f1, auc


def covariance_shift(X_ref, X_test):
    cov = Covariances(estimator='oas')
    ref_covs = cov.transform(X_ref)
    test_covs = cov.transform(X_test)
    return float(distance_riemann(mean_riemann(ref_covs), mean_riemann(test_covs)))


def analyze(subject):
    xfile = OUTPUT_DIR / f'participant_{subject:02d}_X.npy'
    yfile = OUTPUT_DIR / f'participant_{subject:02d}_y.npy'
    sfile = OUTPUT_DIR / f'participant_{subject:02d}_sessions.npy'
    for path in (xfile, yfile, sfile):
        if not path.exists():
            raise FileNotFoundError(f'Missing {path}. Run Step 22 first.')

    X = np.load(xfile)
    y = np.load(yfile, allow_pickle=True)
    sessions = np.load(sfile, allow_pickle=True).astype(str)
    session_ids = sorted(np.unique(sessions).tolist(), key=int)

    print('\n' + '=' * 72)
    print(f'ANALYZING PARTICIPANT {subject}')
    print('=' * 72)
    print(f'X shape: {X.shape}')
    print(f'Sessions found: {session_ids}')

    base = session_ids[0]
    base_mask = sessions == base
    frozen = decoder().fit(X[base_mask], y[base_mask])
    rows, frozen_scores = [], {}

    print('\nRunning frozen Session-0 decoder...')
    for session in session_ids:
        mask = sessions == session
        bal, f1, auc = metrics(frozen, X[mask], y[mask])
        frozen_scores[session] = bal
        rows.append({'participant': subject, 'session': session, 'model': 'frozen',
                     'n_trials': int(mask.sum()), 'balanced_accuracy': bal,
                     'f1': f1, 'auc': auc, 'adaptation_gain': np.nan})
        label = 'training-set reference' if session == base else 'future-session test'
        print(f'Session {session}: n={mask.sum():3d} | balanced accuracy={bal:.3f} | F1={f1:.3f} | AUC={auc:.3f} | {label}')

    print('\nRunning cumulative prior-session decoder...')
    for i, session in enumerate(session_ids[1:], start=1):
        prior = session_ids[:i]
        train_mask = np.isin(sessions, prior)
        test_mask = sessions == session
        adaptive = decoder().fit(X[train_mask], y[train_mask])
        bal, f1, auc = metrics(adaptive, X[test_mask], y[test_mask])
        gain = bal - frozen_scores[session]
        rows.append({'participant': subject, 'session': session, 'model': 'adaptive',
                     'n_trials': int(test_mask.sum()), 'balanced_accuracy': bal,
                     'f1': f1, 'auc': auc, 'adaptation_gain': gain})
        print(f'Test Session {session} | training sessions={prior} | trials={train_mask.sum()} | adaptive={bal:.3f} | frozen={frozen_scores[session]:.3f} | gain={gain:+.3f}')

    print('\nRunning Riemannian covariance-shift audit...')
    drift = []
    for session in session_ids:
        mask = sessions == session
        distance = 0.0 if session == base else covariance_shift(X[base_mask], X[mask])
        drift.append({'participant': subject, 'session': session,
                      'riemannian_covariance_distance': distance,
                      'frozen_balanced_accuracy': frozen_scores[session]})
        print(f'Session {session}: distance={distance:.4f} | frozen={frozen_scores[session]:.3f}')
    return rows, drift


def main():
    print('=' * 72)
    print('NEUROWEAVE EXACT AUDIT: PARTICIPANTS 7 TO 9')
    print('=' * 72)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    all_results, all_drift = [], []
    for subject in PARTICIPANTS:
        results, drift = analyze(subject)
        all_results.extend(results)
        all_drift.extend(drift)

    result_file = RESULTS_DIR / 'participants_7_to_9_exact_session_results.csv'
    drift_file = RESULTS_DIR / 'participants_7_to_9_exact_drift_audit.csv'
    pd.DataFrame(all_results).to_csv(result_file, index=False)
    pd.DataFrame(all_drift).to_csv(drift_file, index=False)
    print(f'\nSaved: {result_file}')
    print(f'Saved: {drift_file}')
    print('Done.')


if __name__ == '__main__':
    main()
