from pathlib import Path
import numpy as np
from moabb.datasets import Kumar2024
from moabb.paradigms import MotorImagery

OUT_DIR = Path("data/processed")
PARTICIPANTS = (7, 8, 9)


def prepare_participant(subject: int) -> None:
    print("\n" + "=" * 72)
    print(f"PREPARING PARTICIPANT {subject}")
    print("=" * 72)
    print(f"Loading participant {subject}...")
    print("The first run may download participant data.")

    dataset = Kumar2024()
    paradigm = MotorImagery()
    X, labels, metadata = paradigm.get_data(dataset=dataset, subjects=[subject])

    # Store labels as integers when possible while preserving the original classes.
    classes, y = np.unique(labels, return_inverse=True)
    sessions = metadata["session"].astype(str).to_numpy()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / f"participant_{subject}.npz"
    np.savez_compressed(
        out_file,
        X=X.astype(np.float32),
        y=y.astype(np.int64),
        sessions=sessions,
        classes=classes,
    )

    print(f"X shape: {X.shape}")
    print(f"Classes: {classes.tolist()}")
    print(f"Sessions found: {sorted(np.unique(sessions).tolist())}")
    print(f"Saved: {out_file}")


def main() -> None:
    print("=" * 72)
    print("NEUROWEAVE MULTI-PARTICIPANT DATA PREPARATION")
    print("=" * 72)
    for subject in PARTICIPANTS:
        prepare_participant(subject)
    print("\nDone preparing participants 7 to 9.")


if __name__ == "__main__":
    main()
