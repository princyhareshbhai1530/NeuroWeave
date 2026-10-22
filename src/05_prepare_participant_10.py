from pathlib import Path
import json

import moabb
import numpy as np
import pandas as pd

from moabb.datasets import Kumar2024
from moabb.paradigms import LeftRightImagery


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

PARTICIPANT = 10


def main():
    print("=" * 72)
    print("NEUROWEAVE PARTICIPANT 10 DATASET PREPARATION")
    print("=" * 72)

    moabb.set_log_level("info")

    dataset = Kumar2024(subjects=[PARTICIPANT])

    paradigm = LeftRightImagery(
        fmin=8,
        fmax=30,
        tmin=0.0,
        tmax=5.0,
        resample=128,
    )

    print(f"\nLoading participant {PARTICIPANT}...")
    print("The first run may download participant data.")

    X, y, metadata = paradigm.get_data(
        dataset=dataset,
        subjects=[PARTICIPANT],
    )

    metadata = metadata.copy()
    metadata["subject"] = metadata["subject"].astype(str)
    metadata["session"] = metadata["session"].astype(str)
    metadata["run"] = metadata["run"].astype(str)

    print("\nData loaded successfully.")
    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")
    print(f"Metadata shape: {metadata.shape}")

    print("\nMetadata columns:")
    print(metadata.columns.tolist())

    print("\nFirst five metadata rows:")
    print(metadata.head().to_string(index=False))

    class_counts = pd.Series(y).value_counts().sort_index()

    print("\nClass distribution:")
    print(class_counts.to_string())

    session_counts = (
        metadata.groupby("session")
        .size()
        .rename("trial_count")
        .reset_index()
    )

    session_class_counts = (
        metadata.assign(label=y)
        .groupby(["session", "label"])
        .size()
        .rename("trial_count")
        .reset_index()
    )

    print("\nTrials per session:")
    print(session_counts.to_string(index=False))

    print("\nTrials per session and class:")
    print(session_class_counts.to_string(index=False))

    unique_sessions = sorted(
        metadata["session"].unique(),
        key=int,
    )

    checks = {
        "participant": PARTICIPANT,
        "n_trials": int(len(y)),
        "n_sessions": int(metadata["session"].nunique()),
        "sessions": unique_sessions,
        "classes": sorted(pd.Series(y).unique().tolist()),
        "x_shape": [int(value) for value in X.shape],
        "contains_nan": bool(np.isnan(X).any()),
        "contains_infinite": bool(np.isinf(X).any()),
        "class_counts": {
            str(label): int(count)
            for label, count in class_counts.items()
        },
        "trials_per_session": {
            str(row["session"]): int(row["trial_count"])
            for _, row in session_counts.iterrows()
        },
    }

    np.save(
        OUTPUT_DIR / "participant_10_X.npy",
        X,
    )

    np.save(
        OUTPUT_DIR / "participant_10_y.npy",
        y,
    )

    metadata.to_csv(
        OUTPUT_DIR / "participant_10_metadata.csv",
        index=False,
    )

    session_counts.to_csv(
        OUTPUT_DIR / "participant_10_session_counts.csv",
        index=False,
    )

    session_class_counts.to_csv(
        OUTPUT_DIR / "participant_10_session_class_counts.csv",
        index=False,
    )

    with open(
        OUTPUT_DIR / "participant_10_readiness.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(checks, file, indent=2)

    print("\nReadiness checks:")
    print(json.dumps(checks, indent=2))

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
            f"Expected sessions {expected_sessions}, "
            f"but found {unique_sessions}."
        )

    if len(checks["classes"]) != 2:
        raise ValueError(
            f"Expected exactly two classes, "
            f"but found {checks['classes']}."
        )

    if checks["contains_nan"]:
        raise ValueError(
            "NaN values were found in the EEG data."
        )

    if checks["contains_infinite"]:
        raise ValueError(
            "Infinite values were found in the EEG data."
        )

    if X.shape[0] != len(y):
        raise ValueError(
            "The EEG tensor and label array have different trial counts."
        )

    if len(y) != len(metadata):
        raise ValueError(
            "The label array and metadata have different trial counts."
        )

    print("\nSaved processed arrays:")
    print(OUTPUT_DIR / "participant_10_X.npy")
    print(OUTPUT_DIR / "participant_10_y.npy")

    print("\nSTATUS: PASS")
    print(
        "Participant 10 is ready for longitudinal analysis."
    )


if __name__ == "__main__":
    main()