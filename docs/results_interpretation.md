# NEUROWEAVE Results Interpretation

## The verdict problem

A BCI score can change for several reasons. NEUROWEAVE does not convert one metric into a biological claim. It compares controlled decoder performance, signal shift, calibration behavior, and missing evidence before returning a bounded verdict.

## Interpretation rules

- Accuracy alone does not measure neuroplasticity.
- A result can support an explanation without proving it.
- Every conclusion must name its strongest competing explanation.
- Missing measurements must be reported as limitations.
- Conflicting evidence produces a mixed or inconclusive verdict.

## Scenario 1: Frozen decoder improves across later sessions

### Possible interpretation

The finding may be consistent with neural adaptation because performance improved without model retraining.

### Evidence needed before favoring neural adaptation

- The decoder was genuinely frozen after Session 0.
- Later-session data were not used to fit preprocessing.
- Task-related EEG patterns became more distinguishable.
- Signal-quality changes do not fully explain improvement.
- Class imbalance and trial counts do not explain improvement.

### Competing explanations

- Recording-interface drift
- Electrode-placement differences
- Noise or artifact changes
- Participant-state differences
- Session-specific experimental differences

### Permitted conclusion

Neural adaptation is better supported, subject to the available signal-quality and drift evidence.

### Prohibited conclusion

Neuroplasticity was detected or proved.

## Scenario 2: Only the cumulative decoder improves

### Possible interpretation

Decoder adaptation is better supported because performance improves after the model receives prior-session data.

### Competing explanations

- The cumulative model receives more training examples.
- The frozen decoder may fail under session distribution shift.
- A shifted decision boundary may explain part of the gain.
- The cumulative model may overfit prior sessions.

### Permitted conclusion

Performance gains depend on prior-session recalibration or cumulative training.

### Prohibited conclusion

The participant's neural patterns did not adapt at all.

## Scenario 3: Performance follows signal-quality changes

### Possible interpretation

Recording-interface or session drift is better supported.

### Evidence to examine

- Channel-level variance
- Missing or unstable channels
- Noise and artifact rates
- Spectral differences
- Session identity predictability
- Sensitivity to unstable-channel removal

### Permitted conclusion

Performance changes are associated with measured recording-quality differences.

### Prohibited conclusion

A specific electrode or material caused the change unless directly measured.

## Scenario 4: Session identity is predictable

### Possible interpretation

Sessions contain strong session-specific structure.

### Why this matters

A model may respond partly to differences between recording sessions rather than differences between motor-imagery classes.

### Permitted conclusion

Session drift is a substantial competing explanation.

### Prohibited conclusion

All task-related neural changes are artificial.

## Scenario 5: Task patterns become more consistent while quality remains stable

### Possible interpretation

The result is consistent with neural adaptation.

### Evidence to examine

- Frozen-decoder performance
- Left-versus-right distinguishability
- Spatial-pattern stability
- Spectral-pattern stability
- Signal-quality measures
- Session-held-out performance

### Permitted conclusion

Neural adaptation is better supported than the measured alternatives.

### Prohibited conclusion

The participant's brain rewired.

## Scenario 6: Metrics or sessions disagree

### Possible interpretation

The evidence is mixed or inconclusive.

### Examples

- Accuracy improves but balanced accuracy does not.
- Some sessions improve while others decline.
- Performance improves alongside major quality changes.
- ROC AUC is strong while hard-decision performance is weak.
- Confidence intervals overlap substantially.

### Permitted conclusion

The current evidence does not clearly separate neural adaptation, decoder adaptation, and session drift.

## Final conclusion

- Better-supported explanation: Decoder adaptation is better supported overall, but its benefit is strongly participant- and session-dependent.
- Evidence: Mean balanced accuracy increased from approximately 0.592 for the frozen decoder to 0.682 for the cumulative decoder. Twelve of twenty future-session comparisons were positive, three were negative, and five were zero. Participants 2 and 11 showed the largest mean gains.
- Strongest competing explanation: Additional training-data volume and session-specific decision-boundary or calibration effects.
- Evidence for the competing explanation: The cumulative decoder used progressively more prior-session data. Participant 11 showed mean ROC AUC of approximately 0.863 but mean frozen balanced accuracy of approximately 0.517, together with strong right-hand prediction bias.
- Session-drift assessment: Covariance distance had inconsistent relationships with frozen performance across participants. The analysis detects session-level signal change but not its physical cause.
- Confidence: Moderate for the descriptive finding that cumulative prior-session training often improved performance. Low for population, protocol, neural-adaptation, or neuroplasticity claims.
- Main limitation: Four selected participants, two per protocol group, unequal training-data volume, and unavailable impedance and placement measurements.
- Required next experiment: Analyze all participants, add uncertainty estimates, and compare against a training-size-matched control. Future collection should record impedance and cap-position information.

## Permitted final wording

In four selected participants, cumulative prior-session training improved mean future-session balanced accuracy relative to a Session-0 frozen decoder, with substantial variation across participants and sessions. The evidence supports participant-specific decoder adaptation while also revealing decision-boundary bias and unresolved session-level drift.

## Claims that must be avoided

- Neuroplasticity was detected.
- The participant's brain rewired.
- A specific electrode caused the change.
- One adaptation protocol is superior.
- The current results generalize to the full dataset or population.
- The system provides a medical diagnosis.

## Bottom line

NEUROWEAVE separated frozen generalization, cumulative decoder adaptation, session-level covariance shift, and hard-decision calibration. Cumulative prior-session training improved performance on average, but the benefit varied across participants and sessions. Participant 11 also demonstrated why accuracy alone can mislead: near-chance hard decisions coexisted with substantially stronger class-ranking performance.
