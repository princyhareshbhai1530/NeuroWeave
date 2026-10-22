from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pyriemann.estimation import Covariances
from pyriemann.utils.distance import distance_riemann
from pyriemann.utils.mean import mean_covariance


OUTPUT_DIR = Path("outputs")


def main():
    print("=" * 72)
    print("NEUROWEAVE SESSION-DRIFT AUDIT")
    print("=" * 72)

    x_path = OUTPUT_DIR / "participant_01_X.npy"
    metadata_path = OUTPUT_DIR / "participant_01_metadata.csv"
    frozen_path = OUTPUT_DIR / "participant_01_frozen_results.csv"
    adaptive_path = OUTPUT_DIR / "participant_01_adaptive_results.csv"

    required_paths = [
        x_path,
        metadata_path,
        frozen_path,
        adaptive_path,
    ]

    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(
                f"Required file not found: {path}"
            )

    X = np.load(x_path)

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

    adaptive_results = pd.read_csv(
        adaptive_path,
        dtype={
            "test_session": str,
        },
    )

    if len(X) != len(metadata):
        raise ValueError(
            "X and metadata trial counts do not match."
        )

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

    print("\nEstimating trial covariance matrices...")

    covariance_estimator = Covariances(
        estimator="oas"
    )

    trial_covariances = (
        covariance_estimator.fit_transform(X)
    )

    print(
        "Trial covariance shape: "
        f"{trial_covariances.shape}"
    )

    session_mean_covariances = {}

    for session in unique_sessions:
        session_mask = sessions == session

        session_mean_covariances[session] = (
            mean_covariance(
                trial_covariances[
                    session_mask
                ],
                metric="riemann",
            )
        )

    reference_covariance = (
        session_mean_covariances["0"]
    )

    session_rows = []

    for session in unique_sessions:
        session_mask = sessions == session
        session_X = X[session_mask]

        trial_rms = np.sqrt(
            np.mean(
                np.square(session_X),
                axis=(1, 2),
            )
        )

        trial_channel_std = np.mean(
            np.std(
                session_X,
                axis=2,
            ),
            axis=1,
        )

        covariance_distance = float(
            distance_riemann(
                reference_covariance,
                session_mean_covariances[
                    session
                ],
            )
        )

        frozen_row = frozen_results[
            frozen_results["test_session"]
            == session
        ]

        if len(frozen_row) != 1:
            raise ValueError(
                "Missing frozen result for "
                f"Session {session}."
            )

        frozen_accuracy = float(
            frozen_row.iloc[0][
                "balanced_accuracy"
            ]
        )

        adaptive_row = adaptive_results[
            adaptive_results["test_session"]
            == session
        ]

        if session == "0":
            adaptive_accuracy = np.nan
        else:
            if len(adaptive_row) != 1:
                raise ValueError(
                    "Missing adaptive result for "
                    f"Session {session}."
                )

            adaptive_accuracy = float(
                adaptive_row.iloc[0][
                    "balanced_accuracy"
                ]
            )

        session_rows.append(
            {
                "participant": 1,
                "session": session,
                "n_trials": int(
                    session_mask.sum()
                ),
                "median_trial_rms": float(
                    np.median(trial_rms)
                ),
                "mean_trial_rms": float(
                    np.mean(trial_rms)
                ),
                "median_channel_std": float(
                    np.median(
                        trial_channel_std
                    )
                ),
                "mean_channel_std": float(
                    np.mean(
                        trial_channel_std
                    )
                ),
                "riemannian_distance_from_session_0": (
                    covariance_distance
                ),
                "frozen_balanced_accuracy": (
                    frozen_accuracy
                ),
                "adaptive_balanced_accuracy": (
                    adaptive_accuracy
                ),
            }
        )

        print(f"\nSession {session}")
        print(
            f"  Trials: {session_mask.sum()}"
        )
        print(
            "  Median trial RMS: "
            f"{np.median(trial_rms):.8f}"
        )
        print(
            "  Median channel STD: "
            f"{np.median(trial_channel_std):.8f}"
        )
        print(
            "  Covariance distance from Session 0: "
            f"{covariance_distance:.4f}"
        )
        print(
            "  Frozen balanced accuracy: "
            f"{frozen_accuracy:.3f}"
        )

    results = pd.DataFrame(
        session_rows
    )

    results_path = (
        OUTPUT_DIR
        / "participant_01_session_drift.csv"
    )

    results.to_csv(
        results_path,
        index=False,
    )

    future_results = results[
        results["session"] != "0"
    ].copy()

    correlation = float(
        future_results[
            "riemannian_distance_from_session_0"
        ].corr(
            future_results[
                "frozen_balanced_accuracy"
            ]
        )
    )

    summary = {
        "participant": 1,
        "reference_session": "0",
        "n_sessions": int(
            len(results)
        ),
        "correlation_between_covariance_distance_and_frozen_accuracy": (
            correlation
        ),
        "largest_covariance_shift_session": str(
            future_results.loc[
                future_results[
                    "riemannian_distance_from_session_0"
                ].idxmax(),
                "session",
            ]
        ),
        "lowest_frozen_accuracy_session": str(
            future_results.loc[
                future_results[
                    "frozen_balanced_accuracy"
                ].idxmin(),
                "session",
            ]
        ),
        "limitations": [
            (
                "Covariance shift does not identify "
                "the physical cause of session drift."
            ),
            (
                "RMS and channel variability are "
                "signal-quality proxies."
            ),
            (
                "Electrode impedance and placement "
                "measurements are unavailable."
            ),
            (
                "The correlation uses only five "
                "future sessions."
            ),
        ],
    }

    summary_path = (
        OUTPUT_DIR
        / "participant_01_session_drift_summary.json"
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

    create_plot(results)

    if len(results) != 6:
        raise ValueError(
            f"Expected six rows, found {len(results)}."
        )

    if not np.isclose(
        results.loc[
            results["session"] == "0",
            "riemannian_distance_from_session_0",
        ].iloc[0],
        0.0,
    ):
        raise ValueError(
            "Session 0 distance should equal zero."
        )

    print("\nSession-drift summary:")
    print(
        json.dumps(
            summary,
            indent=2,
        )
    )

    print("\nSaved outputs:")
    print(results_path)
    print(summary_path)
    print(
        OUTPUT_DIR
        / "participant_01_session_drift.png"
    )

    print("\nSTATUS: PASS")
    print(
        "Session-level signal shifts were measured "
        "without assigning a physical cause."
    )


def create_plot(results):
    plot_data = results.copy()

    plot_data["session"] = (
        plot_data["session"].astype(int)
    )

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(9, 8),
        sharex=True,
    )

    axes[0].plot(
        plot_data["session"],
        plot_data[
            "riemannian_distance_from_session_0"
        ],
        marker="o",
        linewidth=2,
    )

    axes[0].set_ylabel(
        "Riemannian covariance distance"
    )

    axes[0].set_title(
        "Participant 1: Session-Level Signal Shift"
    )

    axes[1].plot(
        plot_data["session"],
        plot_data[
            "frozen_balanced_accuracy"
        ],
        marker="o",
        linewidth=2,
        label="Frozen decoder",
    )

    adaptive_plot = plot_data.dropna(
        subset=[
            "adaptive_balanced_accuracy"
        ]
    )

    axes[1].plot(
        adaptive_plot["session"],
        adaptive_plot[
            "adaptive_balanced_accuracy"
        ],
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
    axes[1].set_xticks(
        plot_data["session"]
    )
    axes[1].set_ylim(0, 1)
    axes[1].legend()

    fig.tight_layout()

    output_path = (
        OUTPUT_DIR
        / "participant_01_session_drift.png"
    )

    fig.savefig(
        output_path,
        dpi=200,
    )

    plt.close(fig)


if __name__ == "__main__":
    main()