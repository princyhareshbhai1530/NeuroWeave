# NEUROWEAVE Prioritized Next Measurements

## Purpose

The next measurements should reduce uncertainty between decoder adaptation, simple training-data volume, decision-boundary effects, session drift, recording-interface change, and explanations that remain compatible with neural adaptation.

## Completed measurement

### Evaluate future sessions with the original frozen decoder

**Status:** Completed for Participants 3–9.

**What it separated:**

- frozen cross-session transfer;
- benefit that appears only after decoder adaptation.

**Observed result:**

Cumulative prior-session retraining improved balanced accuracy on average relative to the frozen Session-0 decoder, but negative and zero outcomes occurred.

## Priority 1: Selective-adaptation policy

### Question

Can NeuroWeave identify when adaptation is likely to help or hurt an unseen session?

### Why this is needed

Seven of 35 future-session comparisons became worse after adaptation, despite a positive average gain.

### Proposed method

- Build a monitoring rule using only information available before or during the unseen session.
- Estimate the expected benefit or risk of adaptation.
- Issue an `adapt`, `do not adapt`, or `insufficient evidence` recommendation.
- Compare the policy against always adapting and never adapting.

### Success condition

Reduce negative adaptation outcomes while retaining most positive gains.

### Feasibility

High.

### Relative cost

Low to medium.

## Priority 2: Training-size-matched control

### Question

Does cumulative adaptation help because it includes multiple session distributions, or simply because it receives more training trials?

### Why this is needed

The cumulative decoder receives progressively more prior-session training data than the frozen decoder.

### Proposed method

For every future test session:

- match the number of training trials across comparison models;
- sample an equal-sized baseline from available earlier data;
- repeat sampling across multiple seeds;
- compare balanced accuracy and uncertainty.

### Success condition

The multi-session adaptive strategy retains an advantage after training volume is controlled.

### Feasibility

High.

### Relative cost

Low.

## Priority 3: Electrode impedance or contact quality

### Question

Do performance and covariance changes follow recording-interface quality?

### What it separates

- recording-interface drift;
- explanations that remain compatible with neural change;
- model adaptation to recording-quality variation.

### Proposed method

Record per-channel impedance or contact-quality measurements before and during every session.

### Success condition

Determine whether performance changes systematically track measured interface-quality changes.

### Feasibility

Medium.

### Relative cost

Low to medium.

### Current dataset availability

Not available in the validated analysis.

## Priority 4: Cap-position or electrode-coordinate metadata

### Question

How sensitive are longitudinal conclusions to physical electrode placement?

### What it separates

- stable task-related patterns;
- cap-repositioning effects;
- channel-specific recording change.

### Proposed method

Record electrode coordinates, cap landmarks, or a standardized placement-quality measure at every session.

### Success condition

Quantify whether spatial placement differences explain part of the observed covariance and performance shift.

### Feasibility

Medium.

### Relative cost

Medium.

## Priority 5: Standardized resting-state baseline

### Question

Are session differences task-specific or part of a general EEG shift?

### What it separates

- task-related change;
- general session drift;
- participant-state effects.

### Proposed method

Collect the same eyes-open and/or eyes-closed resting baseline before every motor-imagery session.

### Success condition

Determine whether changes appear in both resting and task EEG or mainly in the task-specific response.

### Feasibility

Medium.

### Relative cost

Low.

## Priority 6: Repeat a later session without retraining

### Question

Does improvement persist when model parameters remain fixed?

### What it separates

- improved frozen transfer;
- decoder-retraining benefit;
- short-term session variability.

### Proposed method

Repeat a later recording under comparable conditions and evaluate the already-fitted decoder without updating it.

### Success condition

Establish whether the observed change persists without model adaptation.

### Feasibility

High.

### Relative cost

Medium.

## Priority 7: Controlled cap repositioning

### Question

How much performance changes solely because the cap is removed and reapplied?

### What it separates

- stable task-related patterns;
- physical placement sensitivity.

### Proposed method

Record two comparable runs separated by standardized cap removal and repositioning.

### Success condition

Estimate the portion of performance and covariance shift attributable to cap placement.

### Feasibility

Medium.

### Relative cost

Medium.

## Priority 8: Unstable-channel sensitivity analysis

### Question

Does the conclusion depend on a small number of channels?

### What it separates

- distributed task-related information;
- channel-specific recording effects.

### Proposed method

- define channel-instability criteria before examining outcomes;
- remove unstable channels;
- rerun frozen and cumulative analyses;
- compare participant-level gains and uncertainty.

### Success condition

The main conclusion remains similar after unstable-channel removal, or the analysis identifies which channels dominate the result.

### Feasibility

High.

### Relative cost

Low.

## Priority 9: Direct task-pattern analysis

### Question

Do left-hand and right-hand motor-imagery patterns become more stable or distinguishable across sessions?

### What it separates

- decoder-only improvement;
- task-pattern change consistent with learning;
- general recording drift.

### Proposed method

Evaluate:

- class-separation geometry;
- spatial-pattern stability;
- spectral-pattern stability;
- event-related desynchronization lateralization;
- within-class and between-class distances.

### Success condition

Task-related pattern change is demonstrated independently of hard-decision accuracy and recording-quality measures.

### Feasibility

Medium.

### Relative cost

Medium.

## Recommended immediate sequence

```text
1. Training-size-matched control
2. Selective-adaptation policy
3. Unstable-channel sensitivity analysis
4. Collect impedance/contact-quality metadata in new sessions
5. Collect cap-position and resting-state metadata
6. Perform direct task-pattern analysis
```

## Final recommended next measurement

The highest-value combined next step is to evaluate a selective-adaptation policy under a training-size-matched control while collecting electrode/contact-quality metadata in future recordings.
