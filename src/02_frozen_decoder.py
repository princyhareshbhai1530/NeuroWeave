from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pyriemann.classification import MDM
from pyriemann.estimation import Covariances
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.pipeline import make_pipeline


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

TRAIN_SESSION = "0"


def encode_labels(labels):
    label_map = {
        "left_hand": 0,
        "right_hand": 1,
    }

    unknown_labels = set(np.unique(labels)) - set(label_map)

    if unknown_labels:
        raise ValueError(
            f"Unexpected class labels: {unknown_labels}"
        )

    return np.array(
        [label_map[label] for label in labels],
        dtype=int,
    )


def main():
    print("=" * 72)
    print("NEUROWEAVE FROZEN-DECODER BASELINE")
    print("=" * 72)

    x_path = OUTPUT_DIR / "participant_01_X.npy"
    y_path = OUTPUT_DIR / "participant_01_y.npy"
    metadata_path = OUTPUT_DIR / "participant_01_metadata.csv"

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

    if len(X) != len(y_text) or len(X) != len(metadata):
        raise ValueError(
            "X, y and metadata trial counts do not match."
        )

    y = encode_labels(y_text)
    sessions = metadata["session"].to_numpy()

    unique_sessions = sorted(
        np.unique(sessions),
        key=int,
    )

    print(f"\nX shape: {X.shape}")
    print(f"Sessions found: {unique_sessions}")
    print(f"Training session: {TRAIN_SESSION}")

    train_mask = sessions == TRAIN_SESSION

    X_train = X[train_mask]
    y_train = y[train_mask]

    train_counts = dict(
        zip(
            *np.unique(
                y_train,
                return_counts=True,
            )
        )
    )

    print(f"Training trials: {len(y_train)}")
    print(f"Training class counts: {train_counts}")

    if len(y_train) != 80:
        raise ValueError(
            f"Expected 80 Session-0 trials, found {len(y_train)}."
        )

    if set(train_counts) != {0, 1}:
        raise ValueError(
            "Both classes are not present in Session 0."
        )

    pipeline = make_pipeline(
        Covariances(estimator="oas"),
        MDM(metric="riemann"),
    )

    print("\nTraining model on Session 0 only...")
    pipeline.fit(X_train, y_train)
    print("Training complete. Model is now frozen.")

    results = []
    prediction_rows = []

    for session in unique_sessions:
        test_mask = sessions == session

        X_test = X[test_mask]
        y_test = y[test_mask]

        y_pred = pipeline.predict(X_test)

        # MDM transform returns distances to class centroids.
        distances = pipeline.transform(X_test)

        # Class 0 = left_hand and Class 1 = right_hand.
        # Lower distance means greater similarity.
        right_hand_score = (
            distances[:, 0] - distances[:, 1]
        )

        accuracy = accuracy_score(
            y_test,
            y_pred,
        )

        balanced_accuracy = balanced_accuracy_score(
            y_test,
            y_pred,
        )

        macro_f1 = f1_score(
            y_test,
            y_pred,
            average="macro",
        )

        auc = roc_auc_score(
            y_test,
            right_hand_score,
        )

        matrix = confusion_matrix(
            y_test,
            y_pred,
            labels=[0, 1],
        )

        results.append(
            {
                "participant": 1,
                "train_session": TRAIN_SESSION,
                "test_session": session,
                "n_train": len(y_train),
                "n_test": len(y_test),
                "accuracy": accuracy,
                "balanced_accuracy": balanced_accuracy,
                "macro_f1": macro_f1,
                "roc_auc": auc,
                "left_as_left": int(matrix[0, 0]),
                "left_as_right": int(matrix[0, 1]),
                "right_as_left": int(matrix[1, 0]),
                "right_as_right": int(matrix[1, 1]),
            }
        )

        trial_indices = np.where(test_mask)[0]

        for local_index, trial_index in enumerate(
            trial_indices
        ):
            prediction_rows.append(
                {
                    "participant": 1,
                    "train_session": TRAIN_SESSION,
                    "test_session": session,
                    "trial_index": int(trial_index),
                    "true_label": y_text[trial_index],
                    "predicted_label": (
                        "right_hand"
                        if y_pred[local_index] == 1
                        else "left_hand"
                    ),
                    "right_hand_rank_score": float(
                        right_hand_score[local_index]
                    ),
                }
            )

        print(
            f"Session {session}: "
            f"n={len(y_test):3d} | "
            f"accuracy={accuracy:.3f} | "
            f"balanced accuracy={balanced_accuracy:.3f} | "
            f"F1={macro_f1:.3f} | "
            f"AUC={auc:.3f}"
        )

    results_df = pd.DataFrame(results)
    predictions_df = pd.DataFrame(prediction_rows)

    results_path = (
        OUTPUT_DIR
        / "participant_01_frozen_results.csv"
    )

    predictions_path = (
        OUTPUT_DIR
        / "participant_01_frozen_predictions.csv"
    )

    results_df.to_csv(
        results_path,
        index=False,
    )

    predictions_df.to_csv(
        predictions_path,
        index=False,
    )

    future_results = results_df[
        results_df["test_session"] != TRAIN_SESSION
    ]

    summary = {
        "participant": 1,
        "training_session": TRAIN_SESSION,
        "pipeline": "OAS covariance plus Riemannian MDM",
        "training_trials": int(len(y_train)),
        "future_test_sessions": 5,
        "mean_future_balanced_accuracy": float(
            future_results["balanced_accuracy"].mean()
        ),
        "minimum_future_balanced_accuracy": float(
            future_results["balanced_accuracy"].min()
        ),
        "maximum_future_balanced_accuracy": float(
            future_results["balanced_accuracy"].max()
        ),
        "mean_future_auc": float(
            future_results["roc_auc"].mean()
        ),
        "limitations": [
            "Only one participant has been evaluated.",
            "Session 0 performance is training-set performance.",
            "Future-session performance does not prove neuroplasticity.",
            "Electrode impedance is not available in this dataset.",
        ],
    }

    summary_path = (
        OUTPUT_DIR
        / "participant_01_frozen_summary.json"
    )

    with open(
        summary_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
        )

    create_plot(results_df)

    print("\nFuture-session summary:")
    print(json.dumps(summary, indent=2))

    print("\nSaved outputs:")
    print(results_path)
    print(predictions_path)
    print(summary_path)
    print(
        OUTPUT_DIR
        / "participant_01_frozen_trajectory.png"
    )

    if len(results_df) != 6:
        raise ValueError(
            f"Expected six result rows, found {len(results_df)}."
        )

    if len(predictions_df) != len(y):
        raise ValueError(
            "Prediction count does not match trial count."
        )

    print("\nSTATUS: PASS")
    print(
        "The Session-0 decoder was evaluated on "
        "Sessions 1-5 without retraining."
    )


def create_plot(results_df):
    plot_data = results_df.copy()

    plot_data["test_session"] = (
        plot_data["test_session"].astype(int)
    )

    fig, ax = plt.subplots(
        figsize=(9, 5)
    )

    ax.plot(
        plot_data["test_session"],
        plot_data["balanced_accuracy"],
        marker="o",
        linewidth=2,
        label="Frozen decoder",
    )

    ax.axhline(
        0.5,
        color="gray",
        linestyle="--",
        label="Balanced chance level",
    )

    ax.axvline(
        0,
        color="black",
        linestyle=":",
        label="Training session",
    )

    ax.set_title(
        "Participant 1: Frozen Session-0 Decoder"
    )

    ax.set_xlabel("Test session")
    ax.set_ylabel("Balanced accuracy")
    ax.set_xticks(
        plot_data["test_session"]
    )
    ax.set_ylim(0, 1)
    ax.legend()

    fig.tight_layout()

    plot_path = (
        OUTPUT_DIR
        / "participant_01_frozen_trajectory.png"
    )

    fig.savefig(
        plot_path,
        dpi=200,
    )

    plt.close(fig)


if __name__ == "__main__":
    main()
    