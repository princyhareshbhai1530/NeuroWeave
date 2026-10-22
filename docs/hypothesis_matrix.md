# NEUROWEAVE Hypothesis Matrix

## Central question

When motor-imagery decoding performance changes across sessions, is the change more consistent with neural adaptation, decoder adaptation, or recording-interface/session drift?

## Why this question matters

A higher score is not a biological explanation. The same performance change can be produced by a participant learning, a model being recalibrated, or a recording session changing. NEUROWEAVE treats these as competing explanations that must be compared rather than assumed.

## Hypothesis A: Neural adaptation

### Expected observations

- A decoder trained only on Session 0 maintains or improves performance on later sessions.
- Task-related EEG patterns become more consistently distinguishable.
- Improvement remains when the model is not retrained.
- Signal-quality measures do not fully explain the improvement.

### Evidence against this explanation

- Only a retrained decoder improves.
- Performance changes closely follow recording-quality changes.
- Session-specific structure dominates task-related structure.

### Important limitation

These observations would be consistent with neural adaptation but would not directly prove neuroplasticity.

## Hypothesis B: Decoder adaptation

### Expected observations

- A model retrained with prior-session data improves.
- The Session-0 frozen decoder does not show comparable improvement.
- Performance gains depend on recalibration.
- Gains weaken under session-held-out evaluation.

### Evidence against this explanation

- The frozen model improves similarly without access to later-session data.

## Hypothesis C: Recording-interface or session drift

### Expected observations

- Session identity is predictable from signal characteristics.
- Channel-level quality changes across sessions.
- Classifier performance tracks changes in signal quality.
- Noise or channel perturbations reproduce similar performance changes.

### Evidence against this explanation

- Signal-quality indicators remain stable.
- Longitudinal improvement remains after controlling for session effects.

### Important limitation

Without measured electrode impedance or placement metadata, the system cannot directly attribute drift to electrode materials or cap placement.

## Permitted conclusions

- Neural adaptation is better supported.
- Decoder adaptation is better supported.
- Interface or session drift is better supported.
- Evidence is mixed.
- Evidence is inconclusive.

## Prohibited conclusions

- Neuroplasticity was detected.
- The participant's brain rewired.
- A particular electrode caused the change.
- The result proves rehabilitation was successful.
- The system provides a medical diagnosis.
