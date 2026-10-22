# NEUROWEAVE Final Experiment Log

## Experiment status

**Status:** Validated seven-participant frozen-decoder, cumulative prior-session decoder, session-shift, statistical-robustness, and evidence-classification analyses completed.

## Central research question

When motor-imagery decoding performance changes across sessions, is the change more consistent with decoder adaptation, session-level signal shift, or evidence that remains unresolved with the available measurements?

## Experimental objective

1. Evaluate whether a decoder trained only on Session 0 maintains performance when applied unchanged to Sessions 1 through 5.
2. Compare the frozen decoder with a causal cumulative decoder trained only on chronologically earlier sessions.
3. Measure whether cumulative adaptation improves future-session balanced accuracy.
4. quantify uncertainty at the participant level rather than treating repeated sessions as independent participants.
5. Preserve negative and zero adaptation outcomes.
6. Produce a scientifically scoped evidence classification without claiming neuroplasticity or causation.

## Dataset scope

Dataset: Kumar2024 longitudinal left/right motor-imagery EEG dataset.

Full dataset scope:

- Participants available: 18
- Sessions per participant: 6
- Motor-imagery classes: left hand and right hand
- EEG channels: 22
- Original sampling frequency: 512 Hz

Validated NeuroWeave cohort:

- Participant 3
- Participant 4
- Participant 5
- Participant 6
- Participant 7
- Participant 8
- Participant 9

The current inferential result applies only to these seven participants.

## Experimental sessions

Frozen-decoder training session:

- Session 0

Future test sessions:

- Session 1
- Session 2
- Session 3
- Session 4
- Session 5

Each participant contributed five future-session evaluations.

```text
7 participants × 5 future sessions = 35 comparisons
```

## Preprocessing

The final participant arrays used a consistent preprocessing configuration:

```text
Frequency range:      8–30 Hz
Epoch window:         0–5 seconds
Resampling frequency: 128 Hz
EEG channels:         22
Samples per trial:    640
Classes:              left hand and right hand
```

## Decoder configuration

The frozen and cumulative decoders used the same model family.

```text
Covariance estimator: OAS
Feature geometry:     Riemannian tangent space
Classifier:           Linear Discriminant Analysis
LDA shrinkage:        Automatic
Primary metric:       Balanced accuracy
```

## Frozen-decoder protocol

For each participant:

1. Train using Session 0 only.
2. Keep all fitted model parameters unchanged.
3. Evaluate independently on Sessions 1 through 5.
4. Do not use future-session data for retraining or recalibration.

## Cumulative prior-session protocol

For each participant:

```text
Test Session 1 ← train on Session 0
Test Session 2 ← train on Sessions 0–1
Test Session 3 ← train on Sessions 0–2
Test Session 4 ← train on Sessions 0–3
Test Session 5 ← train on Sessions 0–4
```

The current test session was never included in its own training data.

## Leakage and chronology checks

```text
Frozen decoder trained on Session 0 only:              Yes
Frozen decoder updated with future-session data:       No
Current cumulative test session included in training:  No
Current test-session labels used for recalibration:    No
Same decoder family used for both comparisons:         Yes
Direct train-test overlap detected:                    No
```

## Participant-level mean adaptation gains

Adaptation gain is defined as:

```text
adaptive balanced accuracy − frozen balanced accuracy
```

| Participant | Mean adaptation gain | Direction |
|---|---:|---|
| 3 | +0.031954 | Positive |
| 4 | +0.026856 | Positive |
| 5 | −0.016092 | Negative |
| 6 | +0.054869 | Positive |
| 7 | +0.053333 | Positive |
| 8 | +0.058276 | Positive |
| 9 | +0.054138 | Positive |

## Overall descriptive results

```text
Participants:                         7
Future-session comparisons:          35
Mean frozen balanced accuracy:        0.597226
Mean adaptive balanced accuracy:      0.634846
Mean adaptation gain:                 +0.037619
Participant median adaptation gain:   +0.053333
Positive session-level gains:         20
Negative session-level gains:         7
Zero session-level gains:             8
Participants with positive mean gain: 6
Participants with negative mean gain: 1
```

## Statistical robustness

The primary uncertainty analysis resampled participants as clusters so repeated sessions from the same participant were not treated as independent people.

```text
Bootstrap method:                              Participant-clustered
Bootstrap iterations:                          20,000
Random seed:                                   20261021
Clustered bootstrap 95% CI, low:               0.017077
Clustered bootstrap 95% CI, high:              0.052512
Bootstrap probability mean gain is positive:   0.99975
Participant sign-test p-value, two-sided:       0.125
Participant Wilcoxon p-value, two-sided:        0.03125
```

## Leave-one-participant-out sensitivity

The mean adaptation gain remained positive regardless of which participant was removed.

| Excluded participant | Remaining mean gain |
|---|---:|
| 3 | +0.038563 |
| 4 | +0.039413 |
| 5 | +0.046571 |
| 6 | +0.034744 |
| 7 | +0.035000 |
| 8 | +0.034176 |
| 9 | +0.034866 |

## Important counterevidence

The average effect was positive, but adaptation was not universally beneficial.

- Seven future-session comparisons became worse after adaptation.
- Eight comparisons showed zero gain.
- Participant 5 had a negative mean adaptation gain.
- Participant 9 contained both a large negative session-level outcome and a later strong positive outcome.
- The participant sign test did not reach 0.05.
- The cumulative decoder received progressively more prior-session training data, so training-data volume remains a competing explanation.

## Interpretation

The clustered bootstrap interval was entirely above zero, the Wilcoxon test supported a positive participant-level shift, and the leave-one-participant-out result remained positive. These findings support an average adaptation benefit in the studied sample.

The two-sided sign test produced p = 0.125, and negative session-level outcomes remained. The evidence therefore does not support a universal adaptation-benefit claim.

## Final evidence classification

**Support level:** Moderate.

**Evidence status:** Adaptation benefit supported at the studied-sample level.

## Defensible conclusion

Across seven participants and 35 future-session comparisons, cumulative prior-session retraining increased mean balanced accuracy from approximately 0.597 to 0.635. The participant-clustered 95% bootstrap interval for the mean gain was approximately 0.017 to 0.053. Six of seven participants improved on average, but negative and zero session-level outcomes occurred. Adaptation should therefore be monitored and selectively applied rather than assumed beneficial.

## Claims not supported

This experiment does not establish:

- neuroplasticity;
- causal neural adaptation;
- universal benefit from adaptation;
- the physical cause of EEG session drift;
- population-level generalization beyond the studied sample;
- a medical diagnosis or treatment recommendation.

## Final output directory

```text
results/combined_participants_3_to_9/
```

## Final outputs

```text
combined_session_results.csv
paired_future_session_comparisons.csv
participant_summary.csv
overall_summary.csv
participant_mean_gains_for_inference.csv
leave_one_participant_out.csv
statistical_robustness_summary.json
evidence_classification.json
evidence_classification.md
```

## Recommended next experiment

Evaluate a policy that enables adaptation only when held-out or online monitoring predicts benefit. Future data collection should also include electrode impedance or contact-quality measurements and cap-position metadata to help separate recording-interface drift from explanations that remain compatible with neural change.
