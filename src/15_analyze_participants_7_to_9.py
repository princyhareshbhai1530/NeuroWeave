from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.covariance import LedoitWolf
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from pyriemann.estimation import Covariances
from pyriemann.tangentspace import TangentSpace

DATA_DIR = Path("data/processed")
RESULTS_DIR = Path("results")
PARTICIPANTS = (7, 8, 9)


def make_decoder():
    return make_pipeline(
        Covariances(estimator="oas"),
        TangentSpace(metric="riemann"),
        LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto"),
    )


def score(model, X, y):
    pred = model.predict(X)
    bal = balanced_accuracy_score(y, pred)
    f1 = f1_score(y, pred, average="weighted")
    try:
        prob = model.predict_proba(X)[:, 1]
        auc = roc_auc_score(y, prob)
    except Exception:
        auc = np.nan
    return bal, f1, auc


def covariance_distance(X_ref, X_test):
    # Compare participant/session sensor covariance summaries using a stable
    # Frobenius distance. This is a descriptive drift proxy, not a causal test.
    ref = np.mean([LedoitWolf().fit(trial.T).covariance_ for trial in X_ref], axis=0)
    test = np.mean([LedoitWolf().fit(trial.T).covariance_ for trial in X_test], axis=0)
    return float(np.linalg.norm(test - ref, ord="fro"))


def analyze(subject):
    path = DATA_DIR / f"participant_{subject}.npz"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run 14_prepare_participants_7_to_9.py first.")

    d = np.load(path, allow_pickle=True)
    X, y, sessions = d["X"], d["y"], d["sessions"].astype(str)
    session_ids = sorted(np.unique(sessions).tolist(), key=lambda x: int(x))

    print("\n" + "=" * 72)
    print(f"ANALYZING PARTICIPANT {subject}")
    print("=" * 72)
    print(f"X shape: {X.shape}")
    print(f"Sessions found: {session_ids}")

    base = session_ids[0]
    base_mask = sessions == base
    frozen = make_decoder().fit(X[base_mask], y[base_mask])

    rows = []
    print("\nRunning frozen Session-0 decoder...")
    frozen_scores = {}
    for s in session_ids:
        mask = sessions == s
        bal, f1, auc = score(frozen, X[mask], y[mask])
        frozen_scores[s] = bal
        rows.append({"participant": subject, "session": s, "model": "frozen", "balanced_accuracy": bal, "f1": f1, "auc": auc, "adaptation_gain": np.nan})
        print(f"Session {s}: n={mask.sum():3d} | balanced accuracy={bal:.3f} | F1={f1:.3f} | AUC={auc:.3f}")

    print("\nRunning cumulative prior-session decoder...")
    for i, s in enumerate(session_ids[1:], start=1):
        prior = session_ids[:i]
        train_mask = np.isin(sessions, prior)
        test_mask = sessions == s
        adaptive = make_decoder().fit(X[train_mask], y[train_mask])
        bal, f1, auc = score(adaptive, X[test_mask], y[test_mask])
        gain = bal - frozen_scores[s]
        rows.append({"participant": subject, "session": s, "model": "adaptive", "balanced_accuracy": bal, "f1": f1, "auc": auc, "adaptation_gain": gain})
        print(f"Test Session {s} | training sessions={prior} | trials={train_mask.sum()} | adaptive={bal:.3f} | frozen={frozen_scores[s]:.3f} | gain={gain:+.3f}")

    print("\nRunning session covariance-shift analysis...")
    drift_rows = []
    X0 = X[base_mask]
    for s in session_ids:
        mask = sessions == s
        dist = 0.0 if s == base else covariance_distance(X0, X[mask])
        drift_rows.append({"participant": subject, "session": s, "covariance_distance": dist, "frozen_balanced_accuracy": frozen_scores[s]})
        print(f"Session {s}: distance={dist:.4f} | frozen={frozen_scores[s]:.3f}")

    return rows, drift_rows


def main():
    print("=" * 72)
    print("NEUROWEAVE PARTICIPANTS 7 TO 9 COMPLETE AUDIT")
    print("=" * 72)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results, drift = [], []
    for subject in PARTICIPANTS:
        r, d = analyze(subject)
        results.extend(r)
        drift.extend(d)
    pd.DataFrame(results).to_csv(RESULTS_DIR / "participants_7_to_9_session_results.csv", index=False)
    pd.DataFrame(drift).to_csv(RESULTS_DIR / "participants_7_to_9_drift_audit.csv", index=False)
    print("\nSaved results/participants_7_to_9_session_results.csv")
    print("Saved results/participants_7_to_9_drift_audit.csv")
    print("Done.")


if __name__ == "__main__":
    main()
