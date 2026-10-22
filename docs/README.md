# NEUROWEAVE Scientific Evidence Package

## The problem

A brain-computer interface can improve across sessions, but improved accuracy does not reveal why. The participant may be producing more distinguishable motor-imagery patterns, the decoder may be benefiting from recalibration, or the recording conditions may have shifted.

Treating every improvement as neuroplasticity would be scientifically unsafe. Treating every decline as model failure would be equally incomplete.

## What NEUROWEAVE does

NEUROWEAVE is an evidence-and-verdict workflow that separates four questions:

1. Does a Session-0 frozen decoder generalize to later sessions?
2. Does cumulative prior-session retraining improve performance?
3. Do session-level signal characteristics shift?
4. Is weak hard-decision accuracy hiding stronger class-ranking performance?

The system then returns a bounded verdict:

- Neural adaptation is better supported.
- Decoder adaptation is better supported.
- Interface or session drift is better supported.
- Evidence is mixed.
- Evidence is inconclusive.

## Current evidence

The current prototype analyzes Participants 1, 2, 10, and 11 across five future sessions each.

- Mean frozen balanced accuracy: 0.592
- Mean cumulative balanced accuracy: 0.682
- Mean adaptation gain: +0.089
- Session-level outcomes: 12 positive, 3 negative, and 5 zero gains

Cumulative prior-session training improved performance on average, but the benefit varied by participant and session. Participant 11 also showed a substantial difference between class-ranking performance and hard-decision performance, revealing that calibration behavior can materially change the interpretation.

## Scientific boundary

NEUROWEAVE does not claim that neuroplasticity was detected, that a participant's brain rewired, that a specific electrode caused a change, or that the system provides a medical diagnosis.

## Files

- `hypothesis_matrix.md`: Competing explanations and falsifiable observations
- `next_measurements.md`: Follow-up measurements that can separate the explanations
- `prior_art_notes.md`: Evidence base from peer-reviewed research and official documentation
- `experiment_log.md`: Reproducible record of the current four-participant analysis
- `results_interpretation.md`: Verdict rules, limitations, and defensible conclusion

## Why this matters

NEUROWEAVE turns a performance chart into a scientific investigation. Instead of asking only whether accuracy changed, it asks what explanation the available evidence supports, what competing explanation remains, and what measurement should be collected next.
