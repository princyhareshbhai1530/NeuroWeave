import platform
import sys

import mne
import moabb
import numpy as np
import pandas as pd
import sklearn

from moabb.datasets import Kumar2024


def main():
    print("=" * 70)
    print("NEUROWEAVE ENVIRONMENT CHECK")
    print("=" * 70)

    print(f"Python:        {sys.version.split()[0]}")
    print(f"Platform:      {platform.platform()}")
    print(f"MOABB:         {moabb.__version__}")
    print(f"MNE:           {mne.__version__}")
    print(f"NumPy:         {np.__version__}")
    print(f"Pandas:        {pd.__version__}")
    print(f"scikit-learn:  {sklearn.__version__}")

    dataset = Kumar2024(subjects=[1])

    print("\nDataset loader initialized successfully.")
    print(f"Dataset code:  {dataset.code}")
    print(f"Subjects:      {dataset.subject_list}")
    print(f"Sessions:      {dataset.n_sessions}")
    print(f"Paradigm:      {dataset.paradigm}")

    assert dataset.subject_list == [1], (
        "Subject filtering failed. Stop before downloading data."
    )
    assert dataset.n_sessions == 6, (
        f"Expected 6 sessions, found {dataset.n_sessions}."
    )

    print("\nSTATUS: PASS")
    print("The environment and Kumar2024 loader are ready.")


if __name__ == "__main__":
    main()