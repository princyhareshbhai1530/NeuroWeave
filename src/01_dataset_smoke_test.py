from pathlib import Path
import json

import moabb
import numpy as np
import pandas as pd

from moabb.datasets import Kumar2024
from moabb.paradigms import LeftRightImagery


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def main():
    moabb.set_log_level("info")

    print("=" * 70)
    print("NEUROWEAVE DATASET SMOKE TEST")
    print("=" * 70)

    # Critical: begin with one participant only.
    participant = 1
    dataset = Kumar2024(subjects=[participant])

    # The publication and dataset documentation focus on the
    # motor-imagery frequency range.
    paradigm = LeftRightImagery(
        fmin=8,
        fmax=30,
        tmin=0.0,
        tmax=5.0,
        resample=128,
    )

    print(f"\nLoading participant {participant}...")
    print("The first run may download data.")

    X, y, metadata = paradigm.get_data(
        dataset=dataset,
        subjects=[participant],
    )

    print("\nData loaded successfully.")
    print(f"X shape: {X.shape}")
    print(f"y shape: {y.shape}")
    print(f"Metadata shape: {metadata.shape}")

    print("\nMetadata columns:")
    print(metadata.columns.tolist())

    print("\nFirst five metadata rows:")
    print(metadata.head().to_string(index=False))

    print("\nClass distribution:")
    class_counts = pd.Series(y).value_counts().sort_index()
    print(class_counts.to_string())

    session_counts = (
        metadata.groupby(["session"])
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

    checks = {
        "participant": participant,
        "n_trials": int(len(y)),
        "n_sessions": int(metadata["session"].nunique()),
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

    metadata.to_csv(
        OUTPUT_DIR / "participant_01_metadata.csv",
        index=False,
    )

    session_counts.to_csv(
        OUTPUT_DIR / "participant_01_session_counts.csv",
        index=False,
    )

    session_class_counts.to_csv(
        OUTPUT_DIR / "participant_01_session_class_counts.csv",
        index=False,
    )

    with open(
        OUTPUT_DIR / "participant_01_readiness.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(checks, file, indent=2)

    print("\nReadiness checks:")
    print(json.dumps(checks, indent=2))

    assert checks["n_sessions"] == 6, (
        f"Expected 6 sessions, found {checks['n_sessions']}."
    )
    assert len(checks["classes"]) == 2, (
        f"Expected 2 classes, found {checks['classes']}."
    )
    assert not checks["contains_nan"], "NaN values found in EEG tensor."
    assert not checks["contains_infinite"], (
        "Infinite values found in EEG tensor."
    )

    print("\nSTATUS: PASS")
    print("Participant 1 is ready for longitudinal analysis.")
    np.save(OUTPUT_DIR / "participant_01_X.npy", X)
    np.save(OUTPUT_DIR / "participant_01_y.npy", y)

    print("\nSaved processed arrays:")
    print(OUTPUT_DIR / "participant_01_X.npy")
    print(OUTPUT_DIR / "participant_01_y.npy")


if __name__ == "__main__":
    main()