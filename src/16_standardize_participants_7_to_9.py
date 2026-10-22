from pathlib import Path
import numpy as np

DATA_DIR = Path("data/processed")
PARTICIPANTS = (7, 8, 9)
TARGET_SAMPLES = 640


def main():
    print("=" * 72)
    print("NEUROWEAVE STANDARDIZE PARTICIPANTS 7 TO 9")
    print("=" * 72)

    for subject in PARTICIPANTS:
        src = DATA_DIR / f"participant_{subject}.npz"
        if not src.exists():
            raise FileNotFoundError(f"Missing {src}")

        d = np.load(src, allow_pickle=True)
        X = d["X"]
        y = d["y"]
        sessions = d["sessions"]
        classes = d["classes"] if "classes" in d.files else np.unique(y)

        print(f"\nParticipant {subject}")
        print(f"Before: {X.shape}")
        if X.shape[-1] < TARGET_SAMPLES:
            raise ValueError(f"Participant {subject} has only {X.shape[-1]} samples; cannot crop to {TARGET_SAMPLES}.")

        # IMPORTANT: This is a compatibility crop, not resampling. It mirrors the
        # 640-sample tensor length seen in the earlier NeuroWeave participant files.
        X_std = X[..., :TARGET_SAMPLES].astype(np.float32, copy=False)
        dst = DATA_DIR / f"participant_{subject}_standardized.npz"
        np.savez_compressed(dst, X=X_std, y=y, sessions=sessions, classes=classes)

        print(f"After:  {X_std.shape}")
        print(f"Sessions: {sorted(np.unique(sessions.astype(str)).tolist())}")
        print(f"Saved: {dst}")

    print("\nDone. Original participant files were not modified.")
    print("NEXT: verify these 640-sample files against the exact preprocessing used for earlier participants before combining scientific results.")


if __name__ == "__main__":
    main()
