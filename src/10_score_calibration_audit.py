from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pyriemann.classification import MDM
from pyriemann.estimation import Covariances
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.pipeline import make_pipeline


OUTPUT_DIR = Path("outputs")
PARTICIPANTS = [1, 2, 10, 11]


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


def audit_participant(participant):
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

    train_mask = sessions == "0"

    model = create_model()
    model.fit(X[train_mask], y[train_mask])

    rows = []

    for session in ["1", "2", "3", "4", "5"]:
        test_mask = sessions == session

        X_test = X[test_mask]
        y_test = y[test_mask]

        predictions = model.predict(X_test)
        distances = model.transform(X_test)

        right_hand_score = (
            distances[:, 0] - distances[:, 1]
        )

        balanced_accuracy = balanced_accuracy_score(
            y_test,
            predictions,
        )

        auc = roc_auc_score(
            y_test,
            right_hand_score,
        )

        matrix = confusion_matrix(
            y_test,
            predictions,
            labels=[0, 1],
        )

        predicted_right_rate = float(
            np.mean(predictions == 1)
        )

        actual_right_rate = float(
            np.mean(y_test == 1)
        )

        score_mean = float(
            np.mean(right_hand_score)
        )

        score_median = float(
            np.median(right_hand_score)
        )

        score_std = float(
            np.std(right_hand_score)
        )

        rows.append(
            {
                "participant": participant,
                "session": session,
                "n_trials": int(len(y_test)),
                "balanced_accuracy": float(
                    balanced_accuracy
                ),
                "roc_auc": float(auc),
                "auc_minus_balanced_accuracy": float(
                    auc - balanced_accuracy
                ),
                "actual_right_hand_rate": actual_right_rate,
                "predicted_right_hand_rate": (
                    predicted_right_rate
                ),
                "prediction_rate_bias": float(
                    predicted_right_rate
                    - actual_right_rate
                ),
                "right_hand_score_mean": score_mean,
                "right_hand_score_median": score_median,
                "right_hand_score_std": score_std,
                "left_as_left": int(matrix[0, 0]),
                "left_as_right": int(matrix[0, 1]),
                "right_as_left": int(matrix[1, 0]),
                "right_as_right": int(matrix[1, 1]),
            }
        )

        print(
            f"Participant {participant}, Session {session}: "
            f"BA={balanced_accuracy:.3f}, "
            f"AUC={auc:.3f}, "
            f"predicted-right={predicted_right_rate:.3f}, "
            f"actual-right={actual_right_rate:.3f}"
        )

    return pd.DataFrame(rows)


def create_gap_plot(results):
    fig, ax = plt.subplots(figsize=(10, 6))

    for participant in PARTICIPANTS:
        participant_data = results[
            results["participant"] == participant
        ].copy()

        participant_data["session"] = (
            participant_data["session"].astype(int)
        )

        participant_data = participant_data.sort_values(
            "session"
        )

        ax.plot(
            participant_data["session"],
            participant_data[
                "auc_minus_balanced_accuracy"
            ],
            marker="o",
            linewidth=2,
            label=f"Participant {participant}",
        )

    ax.axhline(
        0.0,
        color="black",
        linestyle="--",
        label="AUC equals balanced accuracy",
    )

    ax.set_title(
        "NEUROWEAVE: Ranking vs Hard-Decision Performance"
    )

    ax.set_xlabel("Future session")
    ax.set_ylabel("AUC minus balanced accuracy")
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.legend()

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "four_participant_auc_accuracy_gap.png",
        dpi=200,
    )

    plt.close(fig)


def create_prediction_bias_plot(results):
    fig, ax = plt.subplots(figsize=(10, 6))

    for participant in PARTICIPANTS:
        participant_data = results[
            results["participant"] == participant
        ].copy()

        participant_data["session"] = (
            participant_data["session"].astype(int)
        )

        participant_data = participant_data.sort_values(
            "session"
        )

        ax.plot(
            participant_data["session"],
            participant_data["prediction_rate_bias"],
            marker="o",
            linewidth=2,
            label=f"Participant {participant}",
        )

    ax.axhline(
        0.0,
        color="black",
        linestyle="--",
        label="No prediction-rate bias",
    )

    ax.set_title(
        "NEUROWEAVE: Frozen-Decoder Prediction Bias"
    )

    ax.set_xlabel("Future session")
    ax.set_ylabel(
        "Predicted minus actual right-hand rate"
    )

    ax.set_xticks([1, 2, 3, 4, 5])
    ax.legend()

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "four_participant_prediction_bias.png",
        dpi=200,
    )

    plt.close(fig)


def main():
    print("=" * 72)
    print("NEUROWEAVE SCORE AND PREDICTION-BIAS AUDIT")
    print("=" * 72)

    frames = []

    for participant in PARTICIPANTS:
        participant_results = audit_participant(
            participant
        )

        frames.append(participant_results)

    results = pd.concat(
        frames,
        ignore_index=True,
    )

    participant_summary = (
        results.groupby("participant")
        .agg(
            mean_balanced_accuracy=(
                "balanced_accuracy",
                "mean",
            ),
            mean_roc_auc=(
                "roc_auc",
                "mean",
            ),
            mean_auc_accuracy_gap=(
                "auc_minus_balanced_accuracy",
                "mean",
            ),
            mean_absolute_prediction_bias=(
                "prediction_rate_bias",
                lambda values: float(
                    np.mean(np.abs(values))
                ),
            ),
        )
        .reset_index()
    )

    large_gap_threshold = 0.20
    large_bias_threshold = 0.20

    results["large_auc_accuracy_gap"] = (
        results["auc_minus_balanced_accuracy"]
        >= large_gap_threshold
    )

    results["large_prediction_bias"] = (
        np.abs(results["prediction_rate_bias"])
        >= large_bias_threshold
    )

    summary = {
        "n_participants": len(PARTICIPANTS),
        "n_future_sessions": int(len(results)),
        "large_auc_accuracy_gap_threshold": (
            large_gap_threshold
        ),
        "large_prediction_bias_threshold": (
            large_bias_threshold
        ),
        "sessions_with_large_auc_accuracy_gap": int(
            results["large_auc_accuracy_gap"].sum()
        ),
        "sessions_with_large_prediction_bias": int(
            results["large_prediction_bias"].sum()
        ),
        "limitations": [
            "AUC measures ranking, not calibrated probability.",
            "Balanced accuracy depends on the hard decision boundary.",
            "This audit does not recalibrate using test-session labels.",
            "Thresholds are descriptive prototype rules.",
            "The analysis includes four selected participants.",
        ],
    }

    results.to_csv(
        OUTPUT_DIR
        / "four_participant_score_calibration_audit.csv",
        index=False,
    )

    participant_summary.to_csv(
        OUTPUT_DIR
        / "four_participant_calibration_summary.csv",
        index=False,
    )

    with open(
        OUTPUT_DIR
        / "four_participant_calibration_summary.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
        )

    create_gap_plot(results)
    create_prediction_bias_plot(results)

    print("\nParticipant-level summary:")
    print(
        participant_summary.to_string(
            index=False
        )
    )

    print("\nOverall calibration audit:")
    print(json.dumps(summary, indent=2))

    print("\nSaved outputs:")
    print(
        OUTPUT_DIR
        / "four_participant_score_calibration_audit.csv"
    )
    print(
        OUTPUT_DIR
        / "four_participant_calibration_summary.csv"
    )
    print(
        OUTPUT_DIR
        / "four_participant_calibration_summary.json"
    )
    print(
        OUTPUT_DIR
        / "four_participant_auc_accuracy_gap.png"
    )
    print(
        OUTPUT_DIR
        / "four_participant_prediction_bias.png"
    )

    print("\nSTATUS: PASS")
    print(
        "Ranking performance and hard-decision bias "
        "were audited without test-session recalibration."
    )


if __name__ == "__main__":
    main()