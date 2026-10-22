from pathlib import Path
import json

import moabb
import numpy as np
import pandas as pd

from moabb.datasets import Kumar2024
from moabb.paradigms import LeftRightImagery


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

PARTICIPANTS = [3, 4, 5, 6]


def prepare_participant(participant):
    print("\n" + "=" * 72)
    print(f"PREPARING PARTICIPANT {participant}")
    print("=" * 72)

    dataset = Kumar2024(subjects=[participant])

    paradigm = LeftRightImagery(
        fmin=8,
        fmax=30,
        tmin=0.0,
        tmax=5.0,
        resample=128,
    )

    print(f"\nLoading participant {participant}...")
    print("The first run may download participant data.")

    X, y, metadata = paradigm.get_data(
        dataset=dataset,
        subjects=[participant],
    )

    metadata = metadata.copy()
    metadata["subject"] = metadata["subject"].astype(str)
    metadata["session"] = metadata["session"].astype(str)
    metadata["run"] = metadata["run"].astype(str)

    print("\nData loaded successfully.")
    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")
    print(f"Metadata shape: {metadata.shape}")

    class_counts = (
        pd.Series(y)
        .value_counts()
        .sort_index()
    )

    session_counts = (
        metadata
        .groupby("session")
        .size()
        .rename("trial_count")
        .reset_index()
    )

    session_class_counts = (
        metadata
        .assign(label=y)
        .groupby(["session", "label"])
        .size()
        .rename("trial_count")
        .reset_index()
    )

    print("\nClass distribution:")
    print(class_counts.to_string())

    print("\nTrials per session:")
    print(session_counts.to_string(index=False))

    print("\nTrials per session and class:")
    print(session_class_counts.to_string(index=False))

    unique_sessions = sorted(
        metadata["session"].unique(),
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

    checks = {
        "participant": participant,
        "n_trials": int(len(y)),
        "n_sessions": int(
            metadata["session"].nunique()
        ),
        "sessions": unique_sessions,
        "classes": sorted(
            pd.Series(y).unique().tolist()
        ),
        "x_shape": [
            int(value)
            for value in X.shape
        ],
        "contains_nan": bool(
            np.isnan(X).any()
        ),
        "contains_infinite": bool(
            np.isinf(X).any()
        ),
        "class_counts": {
            str(label): int(count)
            for label, count in class_counts.items()
        },
        "trials_per_session": {
            str(row["session"]): int(
                row["trial_count"]
            )
            for _, row in session_counts.iterrows()
        },
    }

    if unique_sessions != expected_sessions:
        raise ValueError(
            f"Participant {participant}: "
            f"expected sessions {expected_sessions}, "
            f"found {unique_sessions}."
        )

    if len(checks["classes"]) != 2:
        raise ValueError(
            f"Participant {participant}: "
            "expected exactly two classes."
        )

    if checks["contains_nan"]:
        raise ValueError(
            f"Participant {participant}: "
            "NaN values found."
        )

    if checks["contains_infinite"]:
        raise ValueError(
            f"Participant {participant}: "
            "infinite values found."
        )

    if len(X) != len(y):
        raise ValueError(
            f"Participant {participant}: "
            "X and y trial counts differ."
        )

    if len(y) != len(metadata):
        raise ValueError(
            f"Participant {participant}: "
            "y and metadata trial counts differ."
        )

    prefix = f"participant_{participant:02d}"

    np.save(
        OUTPUT_DIR / f"{prefix}_X.npy",
        X,
    )

    np.save(
        OUTPUT_DIR / f"{prefix}_y.npy",
        y,
    )

    metadata.to_csv(
        OUTPUT_DIR / f"{prefix}_metadata.csv",
        index=False,
    )

    session_counts.to_csv(
        OUTPUT_DIR / f"{prefix}_session_counts.csv",
        index=False,
    )

    session_class_counts.to_csv(
        OUTPUT_DIR
        / f"{prefix}_session_class_counts.csv",
        index=False,
    )

    with open(
        OUTPUT_DIR / f"{prefix}_readiness.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            checks,
            file,
            indent=2,
        )

    print("\nReadiness checks:")
    print(json.dumps(checks, indent=2))

    print(
        f"\nParticipant {participant}: STATUS PASS"
    )

    return checks


def main():
    print("=" * 72)
    print("NEUROWEAVE MULTI-PARTICIPANT DATA PREPARATION")
    print("=" * 72)

    moabb.set_log_level("info")

    summaries = []

    for participant in PARTICIPANTS:
        summary = prepare_participant(participant)
        summaries.append(summary)

    summary_path = (
        OUTPUT_DIR
        / "participants_03_06_readiness.json"
    )

    with open(
        summary_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summaries,
            file,
            indent=2,
        )

    print("\n" + "=" * 72)
    print("FINAL STATUS: PASS")
    print("=" * 72)

    print("Prepared participants:")

    for summary in summaries:
        print(
            f"Participant "
            f"{summary['participant']}: "
            f"{summary['n_trials']} trials, "
            f"{summary['n_sessions']} sessions"
        )

    print(
        "\nSaved combined readiness report: "
        f"{summary_path}"
    )


if __name__ == "__main__":
    main()