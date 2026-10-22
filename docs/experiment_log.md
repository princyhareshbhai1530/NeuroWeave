# NEUROWEAVE Experiment Log

## Investigation status

Four-participant frozen-decoder, cumulative prior-session decoder, session-drift, and score-calibration analyses completed.

## The problem being tested

When BCI performance changes across sessions, a conventional accuracy plot cannot reveal whether the participant changed, the decoder changed, or the recording changed. This experiment separates those explanations using controlled decoder comparisons and diagnostic audits.

## Experimental objective

- Evaluate an unchanged Session-0 decoder on Sessions 1 through 5.
- Compare it with a causal cumulative decoder trained only on earlier sessions.
- Audit session-level covariance shift.
- Audit differences between continuous class-ranking performance and hard-decision performance.

## Participants analyzed

- Participant 1
- Participant 2
- Participant 10
- Participant 11

Only four selected participants were analyzed. The findings are descriptive and are not population-level estimates.

## Experimental sessions

- Frozen-decoder training: Session 0
- Future test sessions: Sessions 1, 2, 3, 4, and 5
- Future-session evaluations: 20

## Data configuration

- Classes: Left-hand and right-hand motor imagery
- Session-0 training trials: 80 per participant
- Participants analyzed: 4
- Participants per protocol group: 2
- Population-level protocol comparison: Not permitted

## Verified model configuration

- Feature representation: Trial-level covariance matrices
- Covariance estimator: OAS
- Classifier: Minimum Distance to Mean
- Geometry: Riemannian
- Primary metric: Balanced accuracy
- Additional metrics: Macro F1 and ROC AUC

## Preprocessing details not yet verified

- Epoch window
- Frequency range
- Resampling procedure
- Referencing procedure
- Artifact-removal procedure
- Normalization procedure

These items must remain marked as unverified until traced to the data-preparation pipeline.

## Causal evaluation design

- Session 1 model: trained on Session 0
- Session 2 model: trained on Sessions 0 and 1
- Session 3 model: trained on Sessions 0 through 2
- Session 4 model: trained on Sessions 0 through 3
- Session 5 model: trained on Sessions 0 through 4

The current test session was never included in its own training data.

## Leakage checks

- Frozen model trained on Session 0 only: Yes
- Frozen model updated using future sessions: No
- Current cumulative test session used in training: No
- Test-session labels used for recalibration: No
- Same decoder family used for comparison: Yes
- Direct train-test overlap detected: No

## Participant-level results

### Participant 1

- Protocol: Generic Recentering
- Mean frozen balanced accuracy: 0.600
- Mean cumulative balanced accuracy: 0.613
- Mean gain: +0.013
- Positive / negative / zero sessions: 2 / 1 / 2
- Gain range: -0.033 to +0.082

### Participant 2

- Protocol: Generic Recentering
- Mean frozen balanced accuracy: 0.599
- Mean cumulative balanced accuracy: 0.749
- Mean gain: +0.150
- Positive / negative / zero sessions: 4 / 0 / 1
- Gain range: 0.000 to +0.333

### Participant 10

- Protocol: Personally Assisted Recentering
- Mean frozen balanced accuracy: 0.654
- Mean cumulative balanced accuracy: 0.663
- Mean gain: +0.010
- Positive / negative / zero sessions: 2 / 2 / 1
- Gain range: -0.067 to +0.117

### Participant 11

- Protocol: Personally Assisted Recentering
- Mean frozen balanced accuracy: 0.517
- Mean cumulative balanced accuracy: 0.701
- Mean gain: +0.184
- Positive / negative / zero sessions: 4 / 0 / 1
- Gain range: 0.000 to +0.417

## Overall descriptive results

- Mean frozen balanced accuracy: 0.592
- Mean cumulative balanced accuracy: 0.682
- Mean adaptation gain: +0.089
- Positive session-level gains: 12
- Negative session-level gains: 3
- Zero session-level gains: 5
- Participants with positive mean gain: 4 of 4

## Session-level adaptation gains

### Participant 1

- Session 1: 0.000
- Session 2: +0.017
- Session 3: 0.000
- Session 4: +0.082
- Session 5: -0.033

### Participant 2

- Session 1: 0.000
- Session 2: +0.117
- Session 3: +0.100
- Session 4: +0.333
- Session 5: +0.200

### Participant 10

- Session 1: 0.000
- Session 2: -0.050
- Session 3: +0.049
- Session 4: -0.067
- Session 5: +0.117

### Participant 11

- Session 1: 0.000
- Session 2: +0.283
- Session 3: +0.069
- Session 4: +0.417
- Session 5: +0.150

## Calibration audit

### Participant 1

- Mean frozen balanced accuracy: 0.600
- Mean ROC AUC: 0.651
- Mean AUC-accuracy gap: +0.051
- Mean absolute prediction bias: 0.194

### Participant 2

- Mean frozen balanced accuracy: 0.599
- Mean ROC AUC: 0.654
- Mean AUC-accuracy gap: +0.054
- Mean absolute prediction bias: 0.229

### Participant 10

- Mean frozen balanced accuracy: 0.654
- Mean ROC AUC: 0.709
- Mean AUC-accuracy gap: +0.055
- Mean absolute prediction bias: 0.165

### Participant 11

- Mean frozen balanced accuracy: 0.517
- Mean ROC AUC: 0.863
- Mean AUC-accuracy gap: +0.346
- Mean absolute prediction bias: 0.474

Participant 11 showed a major divergence between ranking and hard-decision performance. The frozen decoder retained substantial ranking information while producing strongly right-hand-biased class predictions.

## Session-drift audit

Correlation between Session-0 covariance distance and frozen balanced accuracy:

- Participant 1: -0.268
- Participant 2: -0.050
- Participant 10: +0.142
- Participant 11: +0.477

The inconsistent direction and magnitude do not support one stable relationship between covariance shift and frozen performance. Covariance distance shows that session structure changed but does not identify a physical or biological cause.

## Unexpected findings

- Participant 11 showed near-chance hard-decision accuracy but strong ROC AUC.
- Participant 10 had negative cumulative gains in Sessions 2 and 4.
- Participant 1 had a negative cumulative gain in Session 5.
- Adaptation did not help every participant in every session.
- Participants 2 and 11 benefited substantially more than Participants 1 and 10.

## Confounders and limitations

- The cumulative decoder used progressively more training data than the frozen decoder.
- Only four selected participants were studied.
- Only two participants represented each protocol group.
- Decision-boundary bias affected some results.
- Electrode impedance was unavailable.
- Cap-placement metadata were unavailable.
- No training-size-matched control was included.
- No population-level statistical inference was performed.

## Produced artifacts

- `four_participant_summary.csv`
- `four_participant_session_results.csv`
- `four_participant_calibration_summary.csv`
- `four_participant_score_calibration_audit.csv`
- `four_participant_decoder_summary.png`
- `four_participant_session_gains.png`
- `four_participant_prediction_bias.png`
- `four_participant_auc_accuracy_gap.png`

## Preliminary interpretation

Cumulative prior-session training improved mean balanced accuracy across the four selected participants, but its benefit varied substantially by participant and session. Decoder adaptation is better supported for the largest improvements, particularly for Participants 2 and 11. However, increased training-data volume and Participant 11's calibration behavior remain important competing explanations.

The current results do not prove neural adaptation, neuroplasticity, rehabilitation success, or the physical cause of recording drift.
