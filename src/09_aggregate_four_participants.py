from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUTPUT_DIR = Path("outputs")
PARTICIPANTS = [1, 2, 10, 11]

PROTOCOL_GROUPS = {
    1: "Generic Recentering",
    2: "Generic Recentering",
    10: "Personally Assisted Recentering",
    11: "Personally Assisted Recentering",
}


def load_participant_results(participant):
    prefix = f"participant_{participant:02d}"

    frozen_path = OUTPUT_DIR / f"{prefix}_frozen_results.csv"
    adaptive_path = OUTPUT_DIR / f"{prefix}_adaptive_results.csv"
    drift_path = OUTPUT_DIR / f"{prefix}_session_drift.csv"

    for path in [frozen_path, adaptive_path, drift_path]:
        if not path.exists():
            raise FileNotFoundError(
                f"Required file not found: {path}"
            )

    frozen = pd.read_csv(
        frozen_path,
        dtype={
            "train_session": str,
            "test_session": str,
        },
    )

    adaptive = pd.read_csv(
        adaptive_path,
        dtype={
            "test_session": str,
        },
    )

    drift = pd.read_csv(
        drift_path,
        dtype={
            "session": str,
        },
    )

    future_frozen = frozen[
        frozen["test_session"] != "0"
    ].copy()

    if len(future_frozen) != 5:
        raise ValueError(
            f"Participant {participant}: expected five "
            f"future frozen results, found {len(future_frozen)}."
        )

    if len(adaptive) != 5:
        raise ValueError(
            f"Participant {participant}: expected five "
            f"adaptive results, found {len(adaptive)}."
        )

    if len(drift) != 6:
        raise ValueError(
            f"Participant {participant}: expected six "
            f"drift rows, found {len(drift)}."
        )

    session_results = adaptive[
        [
            "test_session",
            "balanced_accuracy",
            "frozen_balanced_accuracy",
            "adaptation_gain",
        ]
    ].copy()

    session_results["participant"] = participant
    session_results["protocol_group"] = PROTOCOL_GROUPS[participant]

    session_results = session_results.rename(
        columns={
            "balanced_accuracy": "adaptive_balanced_accuracy",
        }
    )

    future_drift = drift[
        drift["session"] != "0"
    ].copy()

    correlation = future_drift[
        "riemannian_distance_from_session_0"
    ].corr(
        future_drift["frozen_balanced_accuracy"]
    )

    participant_summary = {
        "participant": participant,
        "protocol_group": PROTOCOL_GROUPS[participant],
        "mean_frozen_balanced_accuracy": float(
            future_frozen["balanced_accuracy"].mean()
        ),
        "mean_adaptive_balanced_accuracy": float(
            adaptive["balanced_accuracy"].mean()
        ),
        "mean_adaptation_gain": float(
            adaptive["adaptation_gain"].mean()
        ),
        "minimum_adaptation_gain": float(
            adaptive["adaptation_gain"].min()
        ),
        "maximum_adaptation_gain": float(
            adaptive["adaptation_gain"].max()
        ),
        "sessions_with_positive_gain": int(
            (adaptive["adaptation_gain"] > 0).sum()
        ),
        "sessions_with_negative_gain": int(
            (adaptive["adaptation_gain"] < 0).sum()
        ),
        "sessions_with_zero_gain": int(
            np.isclose(
                adaptive["adaptation_gain"],
                0.0,
            ).sum()
        ),
        "covariance_distance_accuracy_correlation": float(
            correlation
        ),
    }

    return participant_summary, session_results


def create_summary_plot(participant_results):
    participants = participant_results[
        "participant"
    ].astype(str)

    x = np.arange(len(participants))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(
        x - width / 2,
        participant_results[
            "mean_frozen_balanced_accuracy"
        ],
        width,
        label="Frozen Session-0 decoder",
    )

    ax.bar(
        x + width / 2,
        participant_results[
            "mean_adaptive_balanced_accuracy"
        ],
        width,
        label="Cumulative prior-session decoder",
    )

    ax.axhline(
        0.5,
        color="gray",
        linestyle="--",
        label="Balanced chance level",
    )

    ax.set_title(
        "NEUROWEAVE: Cross-Session Decoder Performance"
    )

    ax.set_xlabel("Participant")
    ax.set_ylabel("Mean future-session balanced accuracy")
    ax.set_xticks(x)
    ax.set_xticklabels(participants)
    ax.set_ylim(0, 1)
    ax.legend()

    for index, row in participant_results.iterrows():
        ax.text(
            index,
            max(
                row["mean_frozen_balanced_accuracy"],
                row["mean_adaptive_balanced_accuracy"],
            ) + 0.025,
            f"Gain {row['mean_adaptation_gain']:+.3f}",
            ha="center",
            fontsize=9,
        )

    fig.tight_layout()

    output_path = (
        OUTPUT_DIR
        / "four_participant_decoder_summary.png"
    )

    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def create_session_gain_plot(session_results):
    fig, ax = plt.subplots(figsize=(10, 6))

    for participant in PARTICIPANTS:
        participant_data = session_results[
            session_results["participant"] == participant
        ].copy()

        participant_data["test_session"] = (
            participant_data["test_session"].astype(int)
        )

        participant_data = participant_data.sort_values(
            "test_session"
        )

        ax.plot(
            participant_data["test_session"],
            participant_data["adaptation_gain"],
            marker="o",
            linewidth=2,
            label=f"Participant {participant}",
        )

    ax.axhline(
        0.0,
        color="black",
        linestyle="--",
        label="No adaptation gain",
    )

    ax.set_title(
        "NEUROWEAVE: Session-Level Adaptation Gain"
    )

    ax.set_xlabel("Unseen test session")
    ax.set_ylabel(
        "Cumulative minus frozen balanced accuracy"
    )

    ax.set_xticks([1, 2, 3, 4, 5])
    ax.legend()

    fig.tight_layout()

    output_path = (
        OUTPUT_DIR
        / "four_participant_session_gains.png"
    )

    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main():
    print("=" * 72)
    print("NEUROWEAVE FOUR-PARTICIPANT AGGREGATE ANALYSIS")
    print("=" * 72)

    participant_rows = []
    session_frames = []

    for participant in PARTICIPANTS:
        summary, session_results = load_participant_results(
            participant
        )

        participant_rows.append(summary)
        session_frames.append(session_results)

        print(f"\nParticipant {participant}")
        print(
            "  Mean frozen balanced accuracy:   "
            f"{summary['mean_frozen_balanced_accuracy']:.3f}"
        )
        print(
            "  Mean adaptive balanced accuracy: "
            f"{summary['mean_adaptive_balanced_accuracy']:.3f}"
        )
        print(
            "  Mean adaptation gain:            "
            f"{summary['mean_adaptation_gain']:+.3f}"
        )
        print(
            "  Positive/negative/zero sessions: "
            f"{summary['sessions_with_positive_gain']}/"
            f"{summary['sessions_with_negative_gain']}/"
            f"{summary['sessions_with_zero_gain']}"
        )

    participant_results = pd.DataFrame(
        participant_rows
    ).sort_values("participant")

    session_results = pd.concat(
        session_frames,
        ignore_index=True,
    )

    overall_frozen_mean = float(
        participant_results[
            "mean_frozen_balanced_accuracy"
        ].mean()
    )

    overall_adaptive_mean = float(
        participant_results[
            "mean_adaptive_balanced_accuracy"
        ].mean()
    )

    overall_gain_mean = float(
        participant_results[
            "mean_adaptation_gain"
        ].mean()
    )

    total_positive_sessions = int(
        (session_results["adaptation_gain"] > 0).sum()
    )

    total_negative_sessions = int(
        (session_results["adaptation_gain"] < 0).sum()
    )

    total_zero_sessions = int(
        np.isclose(
            session_results["adaptation_gain"],
            0.0,
        ).sum()
    )

    overall_summary = {
        "participants": PARTICIPANTS,
        "n_participants": len(PARTICIPANTS),
        "n_future_session_evaluations": int(
            len(session_results)
        ),
        "mean_frozen_balanced_accuracy": overall_frozen_mean,
        "mean_adaptive_balanced_accuracy": overall_adaptive_mean,
        "mean_adaptation_gain": overall_gain_mean,
        "sessions_with_positive_gain": total_positive_sessions,
        "sessions_with_negative_gain": total_negative_sessions,
        "sessions_with_zero_gain": total_zero_sessions,
        "participants_with_positive_mean_gain": int(
            (
                participant_results[
                    "mean_adaptation_gain"
                ] > 0
            ).sum()
        ),
        "limitations": [
            "Only four selected participants are included.",
            "Results are descriptive and not population estimates.",
            "Two participants per protocol group are insufficient for group comparison.",
            "Cumulative training uses more data than the frozen decoder.",
            "Decoder improvement does not prove neuroplasticity.",
            "Covariance shift does not identify the physical cause of drift.",
        ],
    }

    participant_results.to_csv(
        OUTPUT_DIR
        / "four_participant_summary.csv",
        index=False,
    )

    session_results.to_csv(
        OUTPUT_DIR
        / "four_participant_session_results.csv",
        index=False,
    )

    with open(
        OUTPUT_DIR
        / "four_participant_summary.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            overall_summary,
            file,
            indent=2,
        )

    create_summary_plot(participant_results)
    create_session_gain_plot(session_results)

    print("\n" + "=" * 72)
    print("OVERALL DESCRIPTIVE SUMMARY")
    print("=" * 72)

    print(
        "Mean frozen balanced accuracy:   "
        f"{overall_frozen_mean:.3f}"
    )

    print(
        "Mean adaptive balanced accuracy: "
        f"{overall_adaptive_mean:.3f}"
    )

    print(
        "Mean adaptation gain:            "
        f"{overall_gain_mean:+.3f}"
    )

    print(
        "Positive/negative/zero session gains: "
        f"{total_positive_sessions}/"
        f"{total_negative_sessions}/"
        f"{total_zero_sessions}"
    )

    print("\nSaved outputs:")
    print(
        OUTPUT_DIR
        / "four_participant_summary.csv"
    )
    print(
        OUTPUT_DIR
        / "four_participant_session_results.csv"
    )
    print(
        OUTPUT_DIR
        / "four_participant_summary.json"
    )
    print(
        OUTPUT_DIR
        / "four_participant_decoder_summary.png"
    )
    print(
        OUTPUT_DIR
        / "four_participant_session_gains.png"
    )

    print("\nSTATUS: PASS")
    print(
        "Four participants were aggregated without "
        "making population-level claims."
    )


if __name__ == "__main__":
    main()