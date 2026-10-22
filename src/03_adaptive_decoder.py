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
    f1_score,
    roc_auc_score,
)
from sklearn.pipeline import make_pipeline


OUTPUT_DIR = Path("outputs")


def encode_labels(labels):
    """Convert text labels into numeric labels."""

    label_map = {
        "left_hand": 0,
        "right_hand": 1,
    }

    unknown_labels = set(np.unique(labels)) - set(label_map)

    if unknown_labels:
        raise ValueError(
            f"Unexpected labels found: {unknown_labels}"
        )

    encoded_labels = np.array(
        [label_map[label] for label in labels],
        dtype=int,
    )

    return encoded_labels


def create_model():
    """Create the covariance and Riemannian MDM decoder."""

    model = make_pipeline(
        Covariances(estimator="oas"),
        MDM(metric="riemann"),
    )

    return model


def create_comparison_plot(results):
    """Plot frozen and cumulative decoder performance."""

    plot_data = results.copy()

    plot_data["test_session"] = (
        plot_data["test_session"].astype(int)
    )

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.plot(
        plot_data["test_session"],
        plot_data["frozen_balanced_accuracy"],
        marker="o",
        linewidth=2,
        label="Frozen Session-0 decoder",
    )

    ax.plot(
        plot_data["test_session"],
        plot_data["balanced_accuracy"],
        marker="s",
        linewidth=2,
        label="Cumulative prior-session decoder",
    )

    ax.axhline(
        0.5,
        color="gray",
        linestyle="--",
        label="Balanced chance level",
    )

    ax.set_title(
        "Participant 1: Frozen vs Causal Adaptive Decoder"
    )

    ax.set_xlabel("Unseen test session")
    ax.set_ylabel("Balanced accuracy")

    ax.set_xticks(
        plot_data["test_session"]
    )

    ax.set_ylim(0, 1)
    ax.legend()

    fig.tight_layout()

    output_path = (
        OUTPUT_DIR
        / "participant_01_decoder_comparison.png"
    )

    fig.savefig(
        output_path,
        dpi=200,
    )

    plt.close(fig)


def main():
    print("=" * 72)
    print("NEUROWEAVE CAUSAL ADAPTIVE-DECODER COMPARISON")
    print("=" * 72)

    x_path = (
        OUTPUT_DIR
        / "participant_01_X.npy"
    )

    y_path = (
        OUTPUT_DIR
        / "participant_01_y.npy"
    )

    metadata_path = (
        OUTPUT_DIR
        / "participant_01_metadata.csv"
    )

    frozen_path = (
        OUTPUT_DIR
        / "participant_01_frozen_results.csv"
    )

    required_paths = [
        x_path,
        y_path,
        metadata_path,
        frozen_path,
    ]

    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(
                f"Required file not found: {path}"
            )

    X = np.load(x_path)

    y_text = np.load(
        y_path,
        allow_pickle=True,
    )

    metadata = pd.read_csv(
        metadata_path,
        dtype={
            "subject": str,
            "session": str,
            "run": str,
        },
    )

    frozen_results = pd.read_csv(
        frozen_path,
        dtype={
            "train_session": str,
            "test_session": str,
        },
    )

    if not (
        len(X) == len(y_text) == len(metadata)
    ):
        raise ValueError(
            "X, y and metadata trial counts do not match."
        )

    y = encode_labels(y_text)

    sessions = (
        metadata["session"]
        .astype(str)
        .to_numpy()
    )

    unique_sessions = sorted(
        np.unique(sessions),
        key=int,
    )

    expected_sessions = [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
    ]

    if unique_sessions != expected_sessions:
        raise ValueError(
            f"Unexpected sessions: {unique_sessions}"
        )

    print(f"\nX shape: {X.shape}")
    print(f"Sessions found: {unique_sessions}")

    print(
        "Evaluation rule: train on previous sessions "
        "and test on the next unseen session."
    )

    result_rows = []
    prediction_rows = []

    for test_session in unique_sessions[1:]:
        test_number = int(test_session)

        training_sessions = [
            session
            for session in unique_sessions
            if int(session) < test_number
        ]

        train_mask = np.isin(
            sessions,
            training_sessions,
        )

        test_mask = (
            sessions == test_session
        )

        if np.any(train_mask & test_mask):
            raise RuntimeError(
                "Data leakage detected."
            )

        X_train = X[train_mask]
        y_train = y[train_mask]

        X_test = X[test_mask]
        y_test = y[test_mask]

        train_counts = dict(
            zip(
                *np.unique(
                    y_train,
                    return_counts=True,
                )
            )
        )

        if set(train_counts) != {0, 1}:
            raise ValueError(
                "Training data does not contain both classes."
            )

        model = create_model()

        model.fit(
            X_train,
            y_train,
        )

        y_pred = model.predict(X_test)

        distances = model.transform(X_test)

        right_hand_score = (
            distances[:, 0]
            - distances[:, 1]
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

        matching_frozen_row = frozen_results[
            frozen_results["test_session"]
            == test_session
        ]

        if len(matching_frozen_row) != 1:
            raise ValueError(
                "Could not find exactly one matching "
                "frozen-decoder result."
            )

        frozen_balanced_accuracy = float(
            matching_frozen_row.iloc[0][
                "balanced_accuracy"
            ]
        )

        adaptation_gain = (
            balanced_accuracy
            - frozen_balanced_accuracy
        )

        result_rows.append(
            {
                "participant": 1,
                "training_sessions": ",".join(
                    training_sessions
                ),
                "test_session": test_session,
                "n_train": int(len(y_train)),
                "n_test": int(len(y_test)),
                "accuracy": float(accuracy),
                "balanced_accuracy": float(
                    balanced_accuracy
                ),
                "macro_f1": float(macro_f1),
                "roc_auc": float(auc),
                "frozen_balanced_accuracy": float(
                    frozen_balanced_accuracy
                ),
                "adaptation_gain": float(
                    adaptation_gain
                ),
            }
        )

        test_indices = np.where(
            test_mask
        )[0]

        for local_index, trial_index in enumerate(
            test_indices
        ):
            predicted_label = (
                "right_hand"
                if y_pred[local_index] == 1
                else "left_hand"
            )

            prediction_rows.append(
                {
                    "participant": 1,
                    "training_sessions": ",".join(
                        training_sessions
                    ),
                    "test_session": test_session,
                    "trial_index": int(
                        trial_index
                    ),
                    "true_label": str(
                        y_text[trial_index]
                    ),
                    "predicted_label": predicted_label,
                    "right_hand_rank_score": float(
                        right_hand_score[
                            local_index
                        ]
                    ),
                }
            )

        print(f"\nTest Session {test_session}")

        print(
            f"  Training sessions: {training_sessions}"
        )

        print(
            f"  Training trials: {len(y_train)}"
        )

        print(
            f"  Test trials: {len(y_test)}"
        )

        print(
            "  Adaptive balanced accuracy: "
            f"{balanced_accuracy:.3f}"
        )

        print(
            "  Frozen balanced accuracy:   "
            f"{frozen_balanced_accuracy:.3f}"
        )

        print(
            "  Adaptation gain:            "
            f"{adaptation_gain:+.3f}"
        )

        print(
            f"  Adaptive AUC: {auc:.3f}"
        )

    results = pd.DataFrame(
        result_rows
    )

    predictions = pd.DataFrame(
        prediction_rows
    )

    results_path = (
        OUTPUT_DIR
        / "participant_01_adaptive_results.csv"
    )

    predictions_path = (
        OUTPUT_DIR
        / "participant_01_adaptive_predictions.csv"
    )

    results.to_csv(
        results_path,
        index=False,
    )

    predictions.to_csv(
        predictions_path,
        index=False,
    )

    positive_gains = int(
        (
            results["adaptation_gain"] > 0
        ).sum()
    )

    negative_gains = int(
        (
            results["adaptation_gain"] < 0
        ).sum()
    )

    zero_gains = int(
        np.isclose(
            results["adaptation_gain"],
            0.0,
        ).sum()
    )

    summary = {
        "participant": 1,
        "evaluation": (
            "Cumulative previous sessions "
            "to next unseen session"
        ),
        "pipeline": (
            "OAS covariance plus Riemannian MDM"
        ),
        "mean_adaptive_balanced_accuracy": float(
            results[
                "balanced_accuracy"
            ].mean()
        ),
        "mean_frozen_balanced_accuracy": float(
            results[
                "frozen_balanced_accuracy"
            ].mean()
        ),
        "mean_adaptation_gain": float(
            results[
                "adaptation_gain"
            ].mean()
        ),
        "sessions_with_positive_gain": (
            positive_gains
        ),
        "sessions_with_negative_gain": (
            negative_gains
        ),
        "sessions_with_zero_gain": (
            zero_gains
        ),
        "limitations": [
            "Only one participant is evaluated.",
            (
                "Cumulative training increases "
                "the available training data."
            ),
            (
                "Improvement does not independently "
                "prove decoder adaptation."
            ),
            (
                "The current test session is never "
                "included in training."
            ),
        ],
    }

    summary_path = (
        OUTPUT_DIR
        / "participant_01_adaptive_summary.json"
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

    create_comparison_plot(results)

    if len(results) != 5:
        raise ValueError(
            f"Expected five result rows, "
            f"found {len(results)}."
        )

    expected_prediction_count = int(
        sum(
            np.sum(sessions == session)
            for session in unique_sessions[1:]
        )
    )

    if len(predictions) != expected_prediction_count:
        raise ValueError(
            "Prediction count does not match "
            "future-session trial count."
        )

    print("\nAdaptive-decoder summary:")

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )

    print("\nSaved outputs:")
    print(results_path)
    print(predictions_path)
    print(summary_path)

    print(
        OUTPUT_DIR
        / "participant_01_decoder_comparison.png"
    )

    print("\nSTATUS: PASS")

    print(
        "Each future session was evaluated "
        "without using that session for training."
    )


if __name__ == "__main__":
    main()