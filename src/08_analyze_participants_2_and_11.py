from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pyriemann.classification import MDM
from pyriemann.estimation import Covariances
from pyriemann.geometry.distance import distance_riemann
from pyriemann.geometry.mean import mean_covariance
from sklearn.metrics import (
    balanced_accuracy_score,
    f1_score,
    roc_auc_score,
)
from sklearn.pipeline import make_pipeline


OUTPUT_DIR = Path("outputs")
PARTICIPANTS = [2, 11]


def encode_labels(labels):
    label_map = {
        "left_hand": 0,
        "right_hand": 1,
    }

    unknown_labels = set(np.unique(labels)) - set(label_map)

    if unknown_labels:
        raise ValueError(
            f"Unexpected labels found: {unknown_labels}"
        )

    return np.array(
        [label_map[label] for label in labels],
        dtype=int,
    )


def create_model():
    return make_pipeline(
        Covariances(estimator="oas"),
        MDM(metric="riemann"),
    )


def calculate_metrics(model, X_test, y_test):
    predictions = model.predict(X_test)
    distances = model.transform(X_test)

    right_hand_score = distances[:, 0] - distances[:, 1]

    return {
        "balanced_accuracy": float(
            balanced_accuracy_score(y_test, predictions)
        ),
        "macro_f1": float(
            f1_score(y_test, predictions, average="macro")
        ),
        "roc_auc": float(
            roc_auc_score(y_test, right_hand_score)
        ),
    }


def run_frozen_analysis(participant, X, y, sessions):
    print("\nRunning frozen Session-0 decoder...")

    train_mask = sessions == "0"
    X_train = X[train_mask]
    y_train = y[train_mask]

    if len(y_train) != 80:
        raise ValueError(
            f"Participant {participant}: expected 80 Session-0 trials, "
            f"found {len(y_train)}."
        )

    model = create_model()
    model.fit(X_train, y_train)

    rows = []

    for session in sorted(np.unique(sessions), key=int):
        test_mask = sessions == session

        metrics = calculate_metrics(
            model,
            X[test_mask],
            y[test_mask],
        )

        rows.append(
            {
                "participant": participant,
                "train_session": "0",
                "test_session": session,
                "n_train": int(len(y_train)),
                "n_test": int(test_mask.sum()),
                **metrics,
            }
        )

        print(
            f"Session {session}: "
            f"n={test_mask.sum():3d} | "
            f"balanced accuracy={metrics['balanced_accuracy']:.3f} | "
            f"F1={metrics['macro_f1']:.3f} | "
            f"AUC={metrics['roc_auc']:.3f}"
        )

    return pd.DataFrame(rows)


def run_adaptive_analysis(
    participant,
    X,
    y,
    sessions,
    frozen_results,
):
    print("\nRunning cumulative prior-session decoder...")

    unique_sessions = sorted(np.unique(sessions), key=int)
    rows = []

    for test_session in unique_sessions[1:]:
        training_sessions = [
            session
            for session in unique_sessions
            if int(session) < int(test_session)
        ]

        train_mask = np.isin(sessions, training_sessions)
        test_mask = sessions == test_session

        if np.any(train_mask & test_mask):
            raise RuntimeError(
                f"Participant {participant}: data leakage detected."
            )

        model = create_model()
        model.fit(X[train_mask], y[train_mask])

        metrics = calculate_metrics(
            model,
            X[test_mask],
            y[test_mask],
        )

        frozen_match = frozen_results[
            frozen_results["test_session"] == test_session
        ]

        if len(frozen_match) != 1:
            raise ValueError(
                f"Participant {participant}: missing frozen result "
                f"for Session {test_session}."
            )

        frozen_accuracy = float(
            frozen_match.iloc[0]["balanced_accuracy"]
        )

        adaptation_gain = (
            metrics["balanced_accuracy"] - frozen_accuracy
        )

        rows.append(
            {
                "participant": participant,
                "training_sessions": ",".join(training_sessions),
                "test_session": test_session,
                "n_train": int(train_mask.sum()),
                "n_test": int(test_mask.sum()),
                **metrics,
                "frozen_balanced_accuracy": frozen_accuracy,
                "adaptation_gain": float(adaptation_gain),
            }
        )

        print(f"\nTest Session {test_session}")
        print(f"  Training sessions: {training_sessions}")
        print(f"  Training trials: {train_mask.sum()}")
        print(
            "  Adaptive balanced accuracy: "
            f"{metrics['balanced_accuracy']:.3f}"
        )
        print(
            "  Frozen balanced accuracy:   "
            f"{frozen_accuracy:.3f}"
        )
        print(
            "  Adaptation gain:            "
            f"{adaptation_gain:+.3f}"
        )

    return pd.DataFrame(rows)


def run_drift_analysis(
    participant,
    X,
    sessions,
    frozen_results,
    adaptive_results,
):
    print("\nRunning session covariance-shift analysis...")

    trial_covariances = Covariances(
        estimator="oas"
    ).fit_transform(X)

    unique_sessions = sorted(np.unique(sessions), key=int)
    mean_covariances = {}

    for session in unique_sessions:
        session_mask = sessions == session

        mean_covariances[session] = mean_covariance(
            trial_covariances[session_mask],
            metric="riemann",
        )

    reference_covariance = mean_covariances["0"]
    rows = []

    for session in unique_sessions:
        session_mask = sessions == session
        session_X = X[session_mask]

        trial_rms = np.sqrt(
            np.mean(np.square(session_X), axis=(1, 2))
        )

        channel_std = np.mean(
            np.std(session_X, axis=2),
            axis=1,
        )

        covariance_distance = float(
            distance_riemann(
                reference_covariance,
                mean_covariances[session],
            )
        )

        frozen_accuracy = float(
            frozen_results.loc[
                frozen_results["test_session"] == session,
                "balanced_accuracy",
            ].iloc[0]
        )

        if session == "0":
            adaptive_accuracy = np.nan
        else:
            adaptive_accuracy = float(
                adaptive_results.loc[
                    adaptive_results["test_session"] == session,
                    "balanced_accuracy",
                ].iloc[0]
            )

        rows.append(
            {
                "participant": participant,
                "session": session,
                "n_trials": int(session_mask.sum()),
                "median_trial_rms": float(
                    np.median(trial_rms)
                ),
                "median_channel_std": float(
                    np.median(channel_std)
                ),
                "riemannian_distance_from_session_0": (
                    covariance_distance
                ),
                "frozen_balanced_accuracy": frozen_accuracy,
                "adaptive_balanced_accuracy": adaptive_accuracy,
            }
        )

        print(
            f"Session {session}: "
            f"distance={covariance_distance:.4f} | "
            f"frozen={frozen_accuracy:.3f}"
        )

    return pd.DataFrame(rows)


def create_participant_plot(
    participant,
    frozen_results,
    adaptive_results,
    drift_results,
):
    frozen_plot = frozen_results.copy()
    adaptive_plot = adaptive_results.copy()
    drift_plot = drift_results.copy()

    frozen_plot["test_session"] = (
        frozen_plot["test_session"].astype(int)
    )

    adaptive_plot["test_session"] = (
        adaptive_plot["test_session"].astype(int)
    )

    drift_plot["session"] = (
        drift_plot["session"].astype(int)
    )

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(9, 8),
        sharex=True,
    )

    axes[0].plot(
        drift_plot["session"],
        drift_plot["riemannian_distance_from_session_0"],
        marker="o",
        linewidth=2,
    )

    axes[0].set_title(
        f"Participant {participant}: "
        "Session Shift and Decoder Performance"
    )

    axes[0].set_ylabel(
        "Riemannian covariance distance"
    )

    future_frozen = frozen_plot[
        frozen_plot["test_session"] > 0
    ]

    axes[1].plot(
        future_frozen["test_session"],
        future_frozen["balanced_accuracy"],
        marker="o",
        linewidth=2,
        label="Frozen Session-0 decoder",
    )

    axes[1].plot(
        adaptive_plot["test_session"],
        adaptive_plot["balanced_accuracy"],
        marker="s",
        linewidth=2,
        label="Cumulative prior-session decoder",
    )

    axes[1].axhline(
        0.5,
        color="gray",
        linestyle="--",
        label="Balanced chance level",
    )

    axes[1].set_xlabel("Session")
    axes[1].set_ylabel("Balanced accuracy")
    axes[1].set_ylim(0, 1)
    axes[1].set_xticks(drift_plot["session"])
    axes[1].legend()

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR
        / f"participant_{participant:02d}_complete_audit.png",
        dpi=200,
    )

    plt.close(fig)


def analyze_participant(participant):
    print("\n" + "=" * 72)
    print(f"ANALYZING PARTICIPANT {participant}")
    print("=" * 72)

    prefix = f"participant_{participant:02d}"

    x_path = OUTPUT_DIR / f"{prefix}_X.npy"
    y_path = OUTPUT_DIR / f"{prefix}_y.npy"
    metadata_path = OUTPUT_DIR / f"{prefix}_metadata.csv"

    for path in [x_path, y_path, metadata_path]:
        if not path.exists():
            raise FileNotFoundError(
                f"Required file not found: {path}"
            )

    X = np.load(x_path)
    y_text = np.load(y_path, allow_pickle=True)

    metadata = pd.read_csv(
        metadata_path,
        dtype={
            "subject": str,
            "session": str,
            "run": str,
        },
    )

    if not (len(X) == len(y_text) == len(metadata)):
        raise ValueError(
            f"Participant {participant}: trial counts differ."
        )

    y = encode_labels(y_text)
    sessions = metadata["session"].astype(str).to_numpy()

    expected_sessions = ["0", "1", "2", "3", "4", "5"]
    unique_sessions = sorted(np.unique(sessions), key=int)

    if unique_sessions != expected_sessions:
        raise ValueError(
            f"Participant {participant}: unexpected sessions "
            f"{unique_sessions}."
        )

    print(f"\nX shape: {X.shape}")
    print(f"Sessions found: {unique_sessions}")

    frozen_results = run_frozen_analysis(
        participant,
        X,
        y,
        sessions,
    )

    adaptive_results = run_adaptive_analysis(
        participant,
        X,
        y,
        sessions,
        frozen_results,
    )

    drift_results = run_drift_analysis(
        participant,
        X,
        sessions,
        frozen_results,
        adaptive_results,
    )

    frozen_results.to_csv(
        OUTPUT_DIR / f"{prefix}_frozen_results.csv",
        index=False,
    )

    adaptive_results.to_csv(
        OUTPUT_DIR / f"{prefix}_adaptive_results.csv",
        index=False,
    )

    drift_results.to_csv(
        OUTPUT_DIR / f"{prefix}_session_drift.csv",
        index=False,
    )

    future_frozen = frozen_results[
        frozen_results["test_session"] != "0"
    ]

    future_drift = drift_results[
        drift_results["session"] != "0"
    ]

    correlation = float(
        future_drift[
            "riemannian_distance_from_session_0"
        ].corr(
            future_drift["frozen_balanced_accuracy"]
        )
    )

    summary = {
        "participant": participant,
        "mean_future_frozen_balanced_accuracy": float(
            future_frozen["balanced_accuracy"].mean()
        ),
        "mean_adaptive_balanced_accuracy": float(
            adaptive_results["balanced_accuracy"].mean()
        ),
        "mean_adaptation_gain": float(
            adaptive_results["adaptation_gain"].mean()
        ),
        "largest_covariance_shift_session": str(
            future_drift.loc[
                future_drift[
                    "riemannian_distance_from_session_0"
                ].idxmax(),
                "session",
            ]
        ),
        "lowest_frozen_accuracy_session": str(
            future_frozen.loc[
                future_frozen[
                    "balanced_accuracy"
                ].idxmin(),
                "test_session",
            ]
        ),
        "correlation_between_covariance_distance_and_frozen_accuracy": (
            correlation
        ),
    }

    with open(
        OUTPUT_DIR / f"{prefix}_complete_summary.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(summary, file, indent=2)

    create_participant_plot(
        participant,
        frozen_results,
        adaptive_results,
        drift_results,
    )

    print("\nParticipant summary:")
    print(json.dumps(summary, indent=2))

    print(f"\nParticipant {participant}: STATUS PASS")

    return summary


def main():
    print("=" * 72)
    print("NEUROWEAVE PARTICIPANTS 2 AND 11 COMPLETE AUDIT")
    print("=" * 72)

    summaries = []

    for participant in PARTICIPANTS:
        summaries.append(
            analyze_participant(participant)
        )

    summary_path = (
        OUTPUT_DIR
        / "participants_02_11_complete_summary.json"
    )

    with open(
        summary_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(summaries, file, indent=2)

    print("\n" + "=" * 72)
    print("FINAL STATUS: PASS")
    print("=" * 72)

    for summary in summaries:
        print(
            f"Participant {summary['participant']}: "
            f"frozen="
            f"{summary['mean_future_frozen_balanced_accuracy']:.3f}, "
            f"adaptive="
            f"{summary['mean_adaptive_balanced_accuracy']:.3f}, "
            f"gain="
            f"{summary['mean_adaptation_gain']:+.3f}"
        )


if __name__ == "__main__":
    main()