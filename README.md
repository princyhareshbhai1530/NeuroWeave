# NeuroWeave

**An evidence-and-verdict engine for investigating longitudinal brain-computer interface (BCI) change.**

NeuroWeave asks a question that raw model accuracy cannot answer on its own:

> **When BCI performance changes across sessions, what changed: the decoder, the recorded signal environment, or evidence we still cannot separate?**

Rather than turning every performance change into a biological claim, NeuroWeave compares frozen and cumulative adaptive decoders, audits session-level signal shift, quantifies uncertainty, surfaces counterexamples, and ends with a cautious evidence verdict plus the next measurement that would reduce uncertainty.

---

## Why NeuroWeave?

Longitudinal EEG-based BCIs operate under non-stationarity. Decoder performance can change across recording sessions, but a change in accuracy alone does not identify its cause.

NeuroWeave structures the investigation around competing explanations:

1. **Decoder adaptation**: does incorporating chronologically prior sessions improve future-session decoding?
2. **Session or recording shift**: is the EEG covariance structure changing across sessions?
3. **Decision-boundary effects**: can ranking information remain useful even when hard predictions deteriorate?
4. **Neural change**: is a neural explanation distinguishable from the available measurements?
5. **Mixed or inconclusive evidence**: when current measurements cannot isolate one explanation, NeuroWeave says so and recommends what to measure next.

The goal is not to make the strongest possible claim. The goal is to make the **strongest defensible claim supported by the available evidence**.

---

## Interactive investigation workflow

The Streamlit dashboard is organized as a scientific investigation:

**Select cohort → Inspect participant → Compare sessions → Weigh evidence → Issue verdict → Recommend next measurement**

The interface includes:

- full-cohort and validated-cohort views
- interactive participant selection
- frozen vs adaptive performance trajectories
- session-level adaptation gains and counterexamples
- participant-level robustness statistics
- explicit supported and unsupported claims
- evidence-to-verdict reasoning
- recommended next measurements
- scientific guardrails against over-interpreting the results

---

## Dataset

NeuroWeave uses the **Kumar2024 longitudinal motor-imagery EEG dataset** through MOABB.

Dataset scope:

- 18 participants
- 6 recording sessions
- left-hand vs right-hand motor imagery
- 22 EEG channels
- source sampling rate: 512 Hz

The current inferential result in this repository is based on the **validated P3–P9 cohort**, comprising seven participants and 35 future-session comparisons. The dashboard keeps the full dataset scope separate from the currently validated evidence cohort.

### Preprocessing used in NeuroWeave

```text
Band-pass:       8–30 Hz
Epoch window:    0–5 s
Resampling:      128 Hz
EEG channels:    22
Task:            left-hand vs right-hand motor imagery
```

The resulting participant tensors use 640 time samples per trial.

---

## Experimental design

### Frozen decoder

For each participant, the baseline decoder is trained on **Session 0** and then evaluated unchanged on future Sessions 1–5.

This tests how well the original decoder transfers as the recording session changes.

### Cumulative adaptive decoder

For each future session, the adaptive decoder trains only on **chronologically earlier sessions**.

Example:

```text
Test Session 1 ← train on Session 0
Test Session 2 ← train on Sessions 0–1
Test Session 3 ← train on Sessions 0–2
Test Session 4 ← train on Sessions 0–3
Test Session 5 ← train on Sessions 0–4
```

The current test session is not included in its own training data.

### Session-shift audit

NeuroWeave also measures covariance shift relative to Session 0 using Riemannian geometry. This acts as a signal-level drift indicator, not a direct measurement of electrode impedance, placement, physiology, or a causal mechanism.

---

## Validated result

Across the current P3–P9 validation cohort:

| Metric | Result |
|---|---:|
| Participants | 7 |
| Future-session comparisons | 35 |
| Mean frozen balanced accuracy | 0.597 |
| Mean adaptive balanced accuracy | 0.635 |
| Mean adaptation gain | +0.038 |
| Positive session-level gains | 20 |
| Negative session-level gains | 7 |
| Zero session-level gains | 8 |
| Participants improving on average | 6 / 7 |

### Participant-level robustness

The participant-clustered bootstrap produced a 95% interval for mean adaptation gain of approximately:

```text
[+0.017, +0.053]
```

Additional participant-level checks:

```text
Wilcoxon two-sided p-value: 0.03125
Sign-test two-sided p-value: 0.125
```

The leave-one-participant-out mean adaptation gain remained positive regardless of which one of the seven participants was excluded.

### NeuroWeave verdict

> **Moderate support for an adaptation benefit within the studied sample.**

Cumulative prior-session retraining improved balanced accuracy on average, but the benefit was **participant- and session-dependent**. Adaptation therefore should not be assumed to help every future session.

---

## What NeuroWeave does not claim

The current analysis does **not** establish:

- neuroplasticity
- a causal neural-adaptation mechanism
- universal benefit from adaptation
- the physical cause of session drift
- population-level generalization beyond the studied cohort
- a medical or neurological diagnosis

NeuroWeave treats these boundaries as part of the product, not as footnotes.

---

## Repository structure

```text
NeuroWeave/
│
├── neuroweave_final_dashboard_fixed.py   # Interactive evidence-and-verdict dashboard
├── requirements.txt                      # Python dependencies
│
├── src/                                  # Preprocessing, experiments and validation scripts
│   ├── ...
│   ├── 22_prepare_participants_7_to_9_exact.py
│   ├── 23_analyze_participants_7_to_9_exact.py
│   ├── 24_combine_participants_3_to_9.py
│   ├── 25_statistical_robustness_participants_3_to_9.py
│   └── 26_generate_evidence_classification.py
│
└── results/
    └── combined_participants_3_to_9/
        ├── combined_session_results.csv
        ├── paired_future_session_comparisons.csv
        ├── participant_summary.csv
        ├── overall_summary.csv
        ├── participant_mean_gains_for_inference.csv
        ├── leave_one_participant_out.csv
        ├── statistical_robustness_summary.json
        ├── evidence_classification.json
        └── evidence_classification.md
```

Raw EEG downloads, local caches, virtual environments, and large intermediate arrays should not be committed to the repository.

---

## Quick start

### 1. Clone the repository

```bash
git clone <YOUR-REPOSITORY-URL>
cd NeuroWeave
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Optional licensed dashboard background

The public repository intentionally does not need to redistribute the licensed Adobe Stock background asset.

To reproduce the local visual experience, place the appropriately licensed file at:

```text
assets/AdobeStock_480629528.mp4
```

The dashboard can still run without this optional visual asset.

### 5. Launch NeuroWeave

```bash
streamlit run neuroweave_final_dashboard_fixed.py
```

---

## Reproducing the validated evidence

The key final-stage scripts are:

```text
22_prepare_participants_7_to_9_exact.py
23_analyze_participants_7_to_9_exact.py
24_combine_participants_3_to_9.py
25_statistical_robustness_participants_3_to_9.py
26_generate_evidence_classification.py
```

The final dashboard reads the validated artifacts stored under:

```text
results/combined_participants_3_to_9/
```

---

## Scientific interpretation

The current evidence supports a narrow but useful conclusion:

> Cumulative prior-session retraining improved future-session balanced accuracy on average in the studied seven-participant cohort, while meaningful negative session-level counterexamples remained.

That finding motivates a more interesting BCI policy than "always adapt":

> **Monitor whether adaptation is likely to help, apply it selectively, and collect additional measurements when competing explanations remain unresolved.**

A particularly valuable next measurement would pair decoding outcomes with recording-quality information such as electrode/contact-quality or impedance metadata. That would make it easier to distinguish recording-interface drift from changes that remain compatible with a neural explanation.

---

## Technology

- Python
- Streamlit
- MOABB
- MNE-Python
- NumPy
- pandas
- scikit-learn
- pyRiemann
- SciPy
- Altair

---

## Data attribution

NeuroWeave uses the Kumar2024 multi-session longitudinal motor-imagery dataset available through MOABB/NEMAR.

Primary publication:

**Kumar et al. (2024), “Transfer learning promotes acquisition of individual BCI skills.”**  
DOI: `10.1093/pnasnexus/pgae076`

Dataset documentation:

- MOABB: https://moabb.neurotechx.com/docs/generated/moabb.datasets.Kumar2024.html
- NEMAR: https://nemar.org/dataset/nm000177

Please follow the original dataset's citation and licensing requirements when reproducing the analysis.

---

## Project status

NeuroWeave is a research prototype designed for scientific investigation and demonstration. The current evidence verdict is explicitly scoped to the validated P3-P9 cohort; additional participants should pass through the same session-aware evaluation and participant-level robustness pipeline before being added to the inferential cohort.

---
