from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUTPUT_DIR = Path("outputs")
PARTICIPANTS = [1, 2, 10, 11]

ADAPTATION_GAIN_THRESHOLD = 0.10
LARGE_AUC_GAP_THRESHOLD = 0.20
LARGE_PREDICTION_BIAS_THRESHOLD = 0.20
STRONG_FROZEN_ACCURACY_THRESHOLD = 0.65
WEAK_FROZEN_ACCURACY_THRESHOLD = 0.55


def load_inputs():
    session_results_path = (
        OUTPUT_DIR
        / "four_participant_session_results.csv"
    )

    calibration_path = (
        OUTPUT_DIR
        / "four_participant_score_calibration_audit.csv"
    )

    required_paths = [
        session_results_path,
        calibration_path,
    ]

    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(
                f"Required file not found: {path}"
            )

    session_results = pd.read_csv(
        session_results_path,
        dtype={
            "test_session": str,
        },
    )

    calibration_results = pd.read_csv(
        calibration_path,
        dtype={
            "session": str,
        },
    )

    return session_results, calibration_results


def load_drift_results():
    frames = []

    for participant in PARTICIPANTS:
        prefix = f"participant_{participant:02d}"

        drift_path = (
            OUTPUT_DIR
            / f"{prefix}_session_drift.csv"
        )

        if not drift_path.exists():
            raise FileNotFoundError(
                f"Required file not found: {drift_path}"
            )

        drift = pd.read_csv(
            drift_path,
            dtype={
                "session": str,
            },
        )

        drift = drift[
            drift["session"] != "0"
        ].copy()

        drift["participant"] = participant

        frames.append(
            drift[
                [
                    "participant",
                    "session",
                    "riemannian_distance_from_session_0",
                ]
            ]
        )

    return pd.concat(
        frames,
        ignore_index=True,
    )


def calculate_participant_relative_drift(drift_results):
    drift_results = drift_results.copy()

    drift_results["relative_drift_percentile"] = (
        drift_results.groupby("participant")[
            "riemannian_distance_from_session_0"
        ].rank(
            method="average",
            pct=True,
        )
    )

    return drift_results


def join_results(
    session_results,
    calibration_results,
    drift_results,
):
    session_results = session_results.copy()

    session_results = session_results.rename(
        columns={
            "test_session": "session",
        }
    )

    combined = session_results.merge(
        calibration_results[
            [
                "participant",
                "session",
                "roc_auc",
                "auc_minus_balanced_accuracy",
                "prediction_rate_bias",
                "actual_right_hand_rate",
                "predicted_right_hand_rate",
            ]
        ],
        on=[
            "participant",
            "session",
        ],
        how="inner",
        validate="one_to_one",
    )

    combined = combined.merge(
        drift_results,
        on=[
            "participant",
            "session",
        ],
        how="inner",
        validate="one_to_one",
    )

    expected_rows = (
        len(PARTICIPANTS) * 5
    )

    if len(combined) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} combined rows, "
            f"found {len(combined)}."
        )

    return combined


def classify_evidence(row):
    adaptation_gain = float(
        row["adaptation_gain"]
    )

    frozen_accuracy = float(
        row["frozen_balanced_accuracy"]
    )

    auc_gap = float(
        row["auc_minus_balanced_accuracy"]
    )

    prediction_bias = abs(
        float(row["prediction_rate_bias"])
    )

    relative_drift = float(
        row["relative_drift_percentile"]
    )

    decoder_adaptation_score = 0
    boundary_failure_score = 0
    session_shift_score = 0
    stable_transfer_score = 0

    reasons = []
    cautions = []

    if adaptation_gain >= ADAPTATION_GAIN_THRESHOLD:
        decoder_adaptation_score += 2

        reasons.append(
            "Cumulative prior-session training improved "
            "balanced accuracy by at least 0.10."
        )

    elif adaptation_gain > 0:
        decoder_adaptation_score += 1

        reasons.append(
            "Cumulative prior-session training produced "
            "a small positive gain."
        )

    elif adaptation_gain < 0:
        cautions.append(
            "Cumulative prior-session training reduced "
            "balanced accuracy."
        )

    if auc_gap >= LARGE_AUC_GAP_THRESHOLD:
        boundary_failure_score += 2

        reasons.append(
            "AUC substantially exceeded hard-decision "
            "balanced accuracy."
        )

    if prediction_bias >= LARGE_PREDICTION_BIAS_THRESHOLD:
        boundary_failure_score += 2

        reasons.append(
            "The frozen decoder showed a large "
            "class-prediction-rate bias."
        )

    if (
        frozen_accuracy <= WEAK_FROZEN_ACCURACY_THRESHOLD
        and float(row["roc_auc"]) >= 0.75
    ):
        boundary_failure_score += 2

        reasons.append(
            "Hard classification was weak while ranking "
            "performance remained informative."
        )

    if relative_drift >= 0.80:
        session_shift_score += 2

        reasons.append(
            "This session was among the participant's "
            "largest covariance shifts."
        )

    elif relative_drift >= 0.60:
        session_shift_score += 1

        reasons.append(
            "This session showed above-median covariance shift."
        )

    if (
        frozen_accuracy >= STRONG_FROZEN_ACCURACY_THRESHOLD
        and prediction_bias < LARGE_PREDICTION_BIAS_THRESHOLD
    ):
        stable_transfer_score += 2

        reasons.append(
            "The frozen Session-0 decoder transferred "
            "with balanced accuracy of at least 0.65."
        )

    elif (
        frozen_accuracy > WEAK_FROZEN_ACCURACY_THRESHOLD
        and prediction_bias < LARGE_PREDICTION_BIAS_THRESHOLD
    ):
        stable_transfer_score += 1

        reasons.append(
            "The frozen decoder transferred above the "
            "weak-performance threshold."
        )

    scores = {
        "decoder_adaptation": decoder_adaptation_score,
        "decision_boundary_failure": boundary_failure_score,
        "session_shift_concern": session_shift_score,
        "stable_frozen_transfer": stable_transfer_score,
    }

    maximum_score = max(
        scores.values()
    )

    leading_categories = [
        category
        for category, score in scores.items()
        if score == maximum_score
        and score > 0
    ]

    if not leading_categories:
        classification = (
            "inconclusive"
        )

    elif len(leading_categories) == 1:
        classification = (
            leading_categories[0]
        )

    else:
        classification = (
            "mixed_evidence"
        )

    if classification == "decoder_adaptation":
        next_measurement = (
            "Evaluate the next session with both the "
            "frozen decoder and the cumulative decoder "
            "without using current-session labels."
        )

    elif classification == "decision_boundary_failure":
        next_measurement = (
            "Collect a small labeled calibration block "
            "or an independent baseline to test whether "
            "the decision boundary can be corrected while "
            "preserving session-level evaluation."
        )

    elif classification == "session_shift_concern":
        next_measurement = (
            "Record electrode impedance, cap placement "
            "and a standardized resting baseline in the "
            "next session."
        )

    elif classification == "stable_frozen_transfer":
        next_measurement = (
            "Repeat the frozen-decoder evaluation in the "
            "next session and verify that signal-quality "
            "indicators remain stable."
        )

    else:
        next_measurement = (
            "Collect both a frozen-decoder control and "
            "recording-quality measurements because the "
            "current evidence does not separate the "
            "competing explanations."
        )

    cautions.append(
        "This classification does not prove neuroplasticity."
    )

    cautions.append(
        "Covariance shift does not identify its physical cause."
    )

    return {
        "classification": classification,
        "decoder_adaptation_score": decoder_adaptation_score,
        "decision_boundary_failure_score": boundary_failure_score,
        "session_shift_concern_score": session_shift_score,
        "stable_frozen_transfer_score": stable_transfer_score,
        "reasons": reasons,
        "cautions": cautions,
        "next_measurement": next_measurement,
    }


def apply_evidence_engine(combined):
    output_rows = []

    for _, row in combined.iterrows():
        evidence = classify_evidence(row)

        output_rows.append(
            {
                "participant": int(
                    row["participant"]
                ),
                "session": str(
                    row["session"]
                ),
                "frozen_balanced_accuracy": float(
                    row[
                        "frozen_balanced_accuracy"
                    ]
                ),
                "adaptive_balanced_accuracy": float(
                    row[
                        "adaptive_balanced_accuracy"
                    ]
                ),
                "adaptation_gain": float(
                    row["adaptation_gain"]
                ),
                "roc_auc": float(
                    row["roc_auc"]
                ),
                "auc_accuracy_gap": float(
                    row[
                        "auc_minus_balanced_accuracy"
                    ]
                ),
                "prediction_rate_bias": float(
                    row["prediction_rate_bias"]
                ),
                "covariance_distance": float(
                    row[
                        "riemannian_distance_from_session_0"
                    ]
                ),
                "relative_drift_percentile": float(
                    row[
                        "relative_drift_percentile"
                    ]
                ),
                "classification": evidence[
                    "classification"
                ],
                "decoder_adaptation_score": evidence[
                    "decoder_adaptation_score"
                ],
                "decision_boundary_failure_score": evidence[
                    "decision_boundary_failure_score"
                ],
                "session_shift_concern_score": evidence[
                    "session_shift_concern_score"
                ],
                "stable_frozen_transfer_score": evidence[
                    "stable_frozen_transfer_score"
                ],
                "reasons": " | ".join(
                    evidence["reasons"]
                ),
                "cautions": " | ".join(
                    evidence["cautions"]
                ),
                "next_measurement": evidence[
                    "next_measurement"
                ],
            }
        )

    return pd.DataFrame(
        output_rows
    )


def create_classification_plot(results):
    classification_order = [
        "decoder_adaptation",
        "decision_boundary_failure",
        "session_shift_concern",
        "stable_frozen_transfer",
        "mixed_evidence",
        "inconclusive",
    ]

    counts = (
        results["classification"]
        .value_counts()
        .reindex(
            classification_order,
            fill_value=0,
        )
    )

    readable_labels = [
        "Decoder\nadaptation",
        "Decision-boundary\nfailure",
        "Session-shift\nconcern",
        "Stable frozen\ntransfer",
        "Mixed\nevidence",
        "Inconclusive",
    ]

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    bars = ax.bar(
        readable_labels,
        counts.values,
    )

    ax.set_title(
        "NEUROWEAVE: Evidence Classification Across Sessions"
    )

    ax.set_xlabel(
        "Evidence classification"
    )

    ax.set_ylabel(
        "Number of participant-sessions"
    )

    ax.set_ylim(
        0,
        max(counts.values) + 2,
    )

    for bar, count in zip(
        bars,
        counts.values,
    ):
        ax.text(
            bar.get_x()
            + bar.get_width() / 2,
            bar.get_height() + 0.1,
            str(int(count)),
            ha="center",
        )

    fig.tight_layout()

    output_path = (
        OUTPUT_DIR
        / "evidence_classification_counts.png"
    )

    fig.savefig(
        output_path,
        dpi=200,
    )

    plt.close(fig)


def create_participant_heatmap(results):
    classification_codes = {
        "decoder_adaptation": 1,
        "decision_boundary_failure": 2,
        "session_shift_concern": 3,
        "stable_frozen_transfer": 4,
        "mixed_evidence": 5,
        "inconclusive": 6,
    }

    matrix = np.zeros(
        (
            len(PARTICIPANTS),
            5,
        )
    )

    text_matrix = []

    for row_index, participant in enumerate(
        PARTICIPANTS
    ):
        participant_data = results[
            results["participant"]
            == participant
        ].copy()

        participant_data["session"] = (
            participant_data["session"]
            .astype(int)
        )

        participant_data = (
            participant_data
            .sort_values("session")
        )

        row_labels = []

        for column_index, (_, row) in enumerate(
            participant_data.iterrows()
        ):
            classification = row[
                "classification"
            ]

            matrix[
                row_index,
                column_index,
            ] = classification_codes[
                classification
            ]

            row_labels.append(
                classification
                .replace("_", "\n")
            )

        text_matrix.append(
            row_labels
        )

    fig, ax = plt.subplots(
        figsize=(11, 6)
    )

    image = ax.imshow(
        matrix,
        aspect="auto",
        vmin=1,
        vmax=6,
        cmap="tab20c",
    )

    ax.set_title(
        "NEUROWEAVE: Session-Level Evidence Map"
    )

    ax.set_xlabel(
        "Future session"
    )

    ax.set_ylabel(
        "Participant"
    )

    ax.set_xticks(
        np.arange(5)
    )

    ax.set_xticklabels(
        [1, 2, 3, 4, 5]
    )

    ax.set_yticks(
        np.arange(
            len(PARTICIPANTS)
        )
    )

    ax.set_yticklabels(
        PARTICIPANTS
    )

    for row_index in range(
        len(PARTICIPANTS)
    ):
        for column_index in range(5):
            ax.text(
                column_index,
                row_index,
                text_matrix[
                    row_index
                ][
                    column_index
                ],
                ha="center",
                va="center",
                fontsize=8,
            )

    colorbar = fig.colorbar(
        image,
        ax=ax,
        ticks=[
            1,
            2,
            3,
            4,
            5,
            6,
        ],
    )

    colorbar.ax.set_yticklabels(
        [
            "Decoder adaptation",
            "Boundary failure",
            "Session shift",
            "Stable transfer",
            "Mixed evidence",
            "Inconclusive",
        ]
    )

    fig.tight_layout()

    output_path = (
        OUTPUT_DIR
        / "participant_session_evidence_map.png"
    )

    fig.savefig(
        output_path,
        dpi=200,
    )

    plt.close(fig)


def main():
    print("=" * 72)
    print("NEUROWEAVE THREE-HYPOTHESIS EVIDENCE ENGINE")
    print("=" * 72)

    (
        session_results,
        calibration_results,
    ) = load_inputs()

    drift_results = load_drift_results()

    drift_results = (
        calculate_participant_relative_drift(
            drift_results
        )
    )

    combined = join_results(
        session_results,
        calibration_results,
        drift_results,
    )

    results = apply_evidence_engine(
        combined
    )

    results_path = (
        OUTPUT_DIR
        / "session_evidence_classifications.csv"
    )

    results.to_csv(
        results_path,
        index=False,
    )

    classification_counts = (
        results["classification"]
        .value_counts()
        .to_dict()
    )

    summary = {
        "n_participants": int(
            results["participant"].nunique()
        ),
        "n_participant_sessions": int(
            len(results)
        ),
        "thresholds": {
            "adaptation_gain": (
                ADAPTATION_GAIN_THRESHOLD
            ),
            "large_auc_gap": (
                LARGE_AUC_GAP_THRESHOLD
            ),
            "large_prediction_bias": (
                LARGE_PREDICTION_BIAS_THRESHOLD
            ),
            "strong_frozen_accuracy": (
                STRONG_FROZEN_ACCURACY_THRESHOLD
            ),
            "weak_frozen_accuracy": (
                WEAK_FROZEN_ACCURACY_THRESHOLD
            ),
        },
        "classification_counts": {
            str(key): int(value)
            for key, value
            in classification_counts.items()
        },
        "limitations": [
            "The rules are transparent prototype heuristics.",
            "Thresholds are not clinically validated.",
            "The engine does not detect neuroplasticity.",
            "The engine does not identify the physical cause of drift.",
            "The analysis includes four selected participants.",
        ],
    }

    summary_path = (
        OUTPUT_DIR
        / "evidence_engine_summary.json"
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

    create_classification_plot(
        results
    )

    create_participant_heatmap(
        results
    )

    print("\nSession classifications:")

    print(
        results[
            [
                "participant",
                "session",
                "classification",
                "adaptation_gain",
                "auc_accuracy_gap",
                "prediction_rate_bias",
                "relative_drift_percentile",
            ]
        ].to_string(
            index=False
        )
    )

    print("\nEvidence-engine summary:")
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
        / "evidence_classification_counts.png"
    )

    print(
        OUTPUT_DIR
        / "participant_session_evidence_map.png"
    )

    print("\nSTATUS: PASS")

    print(
        "Every participant-session received a "
        "transparent evidence classification."
    )


if __name__ == "__main__":
    main()