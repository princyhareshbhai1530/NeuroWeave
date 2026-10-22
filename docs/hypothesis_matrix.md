# NEUROWEAVE Hypothesis Matrix

## Central question

When motor-imagery decoding performance changes across sessions, is the change more consistent with neural adaptation, decoder adaptation, recording-interface/session drift, decision-boundary effects, or evidence that remains unresolved?

## Hypothesis A: Neural adaptation

### Expected observations

- A decoder trained only on Session 0 maintains or improves performance on later sessions.
- Task-related EEG patterns become more consistently distinguishable.
- Improvement remains when the model is not retrained.
- Signal-quality measurements do not explain the improvement.
- Task-specific changes are stronger than changes in a standardized resting baseline.

### Evidence against or limiting this explanation

- Improvement appears only after decoder retraining.
- Performance changes closely follow recording-quality changes.
- Session-specific structure dominates task-related structure.
- The frozen decoder deteriorates while only the adaptive model improves.
- Impedance, cap position, resting-state, or direct task-pattern evidence is missing.

### Important limitation

Observations may be consistent with neural adaptation but do not directly prove neuroplasticity.

### Current evidence status

**Not established.**

The validated experiment does not include sufficient direct neural-pattern, impedance, cap-position, or resting-state evidence to isolate neural adaptation from modelling and recording-session effects.

## Hypothesis B: Decoder adaptation

### Expected observations

- A model retrained with chronologically prior sessions improves future-session decoding.
- The Session-0 frozen decoder does not show comparable improvement.
- Performance gains depend on recalibration or exposure to multiple session distributions.
- The benefit remains under session-held-out evaluation.
- Participant-aware uncertainty estimates support a positive average gain.

### Evidence against or limiting this explanation

- The frozen decoder improves similarly without later-session training.
- Adaptation frequently makes unseen-session performance worse.
- Gains disappear under a training-size-matched control.
- Improvement is explained entirely by greater training-data volume.

### Observed supporting evidence

Across seven participants and 35 future-session comparisons:

- mean balanced accuracy increased from 0.597226 to 0.634846;
- mean adaptation gain was +0.037619;
- six of seven participants improved on average;
- 20 future-session comparisons improved;
- the participant-clustered 95% bootstrap interval was [0.017077, 0.052512];
- the participant Wilcoxon p-value was 0.03125;
- leave-one-participant-out mean gains remained positive.

### Observed counterevidence

- seven future-session comparisons became worse;
- eight comparisons showed zero gain;
- Participant 5 had a negative mean gain of −0.016092;
- the participant sign-test p-value was 0.125;
- the cumulative decoder received progressively more training data.

### Current evidence status

**Moderately supported at the studied-sample level.**

## Hypothesis C: Recording-interface or session drift

### Expected observations

- Session identity is predictable from signal characteristics.
- Channel-level quality changes across sessions.
- Classifier performance tracks measured signal quality.
- Noise or channel perturbations reproduce similar performance changes.
- Covariance structure changes relative to Session 0.
- Results depend strongly on unstable channels or cap placement.

### Evidence against or limiting this explanation

- Direct recording-quality measures remain stable.
- Longitudinal improvement remains after controlling for session effects.
- Results persist after unstable-channel removal.
- Task-related changes appear without corresponding resting-state or quality changes.

### Important limitation

Without measured electrode impedance, contact quality, or placement metadata, NeuroWeave cannot identify the physical source of session drift.

### Current evidence status

**Plausible but unresolved.**

The current analysis detects session-level signal change but does not identify whether it arose from electrode contact, cap placement, participant state, neural change, or another session factor.

## Hypothesis D: Decision-boundary or calibration effect

### Expected observations

- Balanced accuracy is weak while ROC AUC or ranking quality remains stronger.
- Predictions are biased toward one class.
- Recalibration improves hard-decision performance without substantially changing ranking.
- Threshold changes explain part of the apparent performance deterioration.

### Evidence against or limiting this explanation

- Ranking and hard-decision metrics deteriorate together.
- Prediction rates remain balanced.
- Recalibration does not improve performance.

### Current evidence status

**Important competing mechanism, but not the primary final explanation.**

Decision-boundary effects should be monitored because weak hard-decision performance does not necessarily imply that all discriminative information disappeared.

## Permitted conclusions

NeuroWeave may conclude that:

- decoder adaptation is better supported;
- frozen transfer is stable for a participant or session;
- recording/session drift is a substantial competing explanation;
- decision-boundary failure is plausible;
- evidence is mixed;
- evidence is inconclusive;
- the tested adaptation strategy provides an average benefit within the studied sample.

## Prohibited conclusions

NeuroWeave must not conclude that:

- neuroplasticity was detected;
- a participant's brain rewired;
- a particular electrode caused the change without direct measurement;
- adaptation helps every participant or session;
- the result generalizes to the full population;
- rehabilitation was proved successful;
- the system provides a medical diagnosis.

## Final evidence classification

**Moderate support for an adaptation benefit within the validated P3–P9 sample.**

The average adaptation gain is positive and participant-aware robustness checks support that direction. However, adaptation is not universally beneficial, session-level losses remain, and neural and recording-interface causes remain unresolved.

## Resulting operational policy

Do not enable adaptation blindly.

Use monitoring evidence to decide when adaptation is likely to help, preserve counterexamples, and request additional measurements when the cause of longitudinal change cannot be separated.
