# Candidate Follow-Up Measurements

## Purpose

The current analysis can rank competing explanations, but some causes cannot be separated without additional measurements. The following measurements are prioritized by scientific value, feasibility, and cost.

## 1. Evaluate later sessions with the original frozen decoder

Separates:
- Neural adaptation
- Decoder adaptation

If neural adaptation is better supported:
- Later-session patterns may become more recognizable without retraining.

If decoder adaptation is better supported:
- Improvement may appear only after the decoder is updated.

Feasibility: High
Relative cost: Low
Status: Completed for four selected participants

## 2. Record electrode impedance for every session

Separates:
- Neural adaptation
- Recording-interface drift

Possible contribution:
- Determines whether performance changes follow interface-quality changes.

Feasibility: Medium
Relative cost: Low to medium
Dataset availability: Not currently available

## 3. Record a standardized resting baseline

Separates:
- Task-related change
- General session drift

Possible contribution:
- Tests whether session differences also appear outside the motor-imagery task.

Feasibility: Medium
Relative cost: Low
Dataset availability: Must be verified

## 4. Repeat a later session without retraining

Separates:
- Neural adaptation
- Decoder adaptation

Possible contribution:
- Tests whether improvement persists when model parameters remain fixed.

Feasibility: High
Relative cost: Medium

## 5. Repeat after electrode-cap repositioning

Separates:
- Stable neural patterns
- Interface or placement sensitivity

Possible contribution:
- Tests how dependent the conclusion is on the physical recording setup.

Feasibility: Medium
Relative cost: Medium

## 6. Remove unstable channels and rerun the analysis

Separates:
- Distributed task-related change
- Channel-specific recording effects

Possible contribution:
- Tests whether the conclusion depends heavily on a small number of channels.

Feasibility: High
Relative cost: Low

## Recommended next experiment

Expand the frozen, cumulative, drift, and calibration analyses to all participants. Add participant-held-out uncertainty estimates and a training-size-matched control so that the effect of adaptation can be separated from the effect of simply providing more training data.
