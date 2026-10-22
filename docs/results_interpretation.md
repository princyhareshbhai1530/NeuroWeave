# NEUROWEAVE Results Interpretation

## Interpretation rules

1. Accuracy alone does not measure neuroplasticity.
2. A result can support an explanation without proving it.
3. All conclusions must consider competing explanations.
4. Missing measurements must be reported as limitations.
5. Negative and zero adaptation outcomes must remain visible.
6. Repeated sessions from one participant must not be treated as independent participants.
7. If evidence conflicts, the conclusion must preserve that uncertainty.

## Scenario 1: Frozen decoder improves across later sessions

### Possible interpretation

The result may be consistent with increasingly recognizable or stable task-related patterns because performance improved without retraining.

### Evidence required before favoring a neural explanation

- The decoder was genuinely frozen after Session 0.
- No future-session data were used to fit preprocessing or model parameters.
- Task-related EEG patterns became more consistently distinguishable.
- Signal-quality changes did not explain the improvement.
- Improvement was not caused by class imbalance or trial-count differences.

### Competing explanations

- recording-interface drift;
- electrode-placement differences;
- changes in noise or artifacts;
- participant-state differences;
- session-specific experimental differences.

### Permitted conclusion

The result is consistent with improved frozen transfer, subject to signal-quality and session-drift evidence.

### Prohibited conclusion

Neuroplasticity was detected or proved.

## Scenario 2: Only the adaptive decoder improves

### Possible interpretation

Decoder adaptation is better supported because performance improves only after the model receives chronologically prior session data.

### Competing explanations

- additional training-data volume;
- greater session diversity in the training set;
- overfitting to later-session distributions;
- decision-boundary or calibration effects;
- recording-quality differences.

### Permitted conclusion

Future-session performance depends partly on decoder recalibration or adaptation.

### Prohibited conclusion

The participant's brain did not adapt.

## Scenario 3: Performance follows signal-quality changes

### Possible interpretation

Recording-interface or broader session drift becomes a stronger explanation.

### Evidence to examine

- electrode impedance or contact quality;
- electrode placement;
- channel-level variance;
- unstable or missing channels;
- noise and artifact levels;
- spectral differences;
- session identity predictability;
- sensitivity to unstable-channel removal.

### Permitted conclusion

Performance changes are associated with measured recording-quality differences.

### Prohibited conclusion

A particular electrode or electrode material caused the change unless that cause was measured directly.

## Scenario 4: Session identity is highly predictable

### Possible interpretation

Later sessions contain strong session-specific structure.

### Why this matters

A decoder may respond partly to differences between recording sessions instead of only to differences between motor-imagery classes.

### Permitted conclusion

Session drift is a substantial competing explanation.

### Prohibited conclusion

All task-related neural changes are artificial.

## Scenario 5: Task-related patterns become more consistent while quality remains stable

### Possible interpretation

The result may be consistent with neural adaptation.

### Evidence to examine

- frozen-decoder transfer;
- left-versus-right class distinguishability;
- stability of task-related spatial patterns;
- stability of task-related spectral patterns;
- recording-quality measures;
- session-held-out performance;
- resting-state changes.

### Permitted conclusion

Neural adaptation may be better supported than the measured alternatives.

### Prohibited conclusion

The participant's brain rewired or neuroplasticity was proved.

## Scenario 6: Results differ across sessions, participants, or metrics

### Possible interpretation

The effect is heterogeneous, mixed, or incompletely explained.

### Examples

- some future sessions improve while others decline;
- mean performance improves while a participant worsens;
- ranking performance remains useful despite biased hard decisions;
- performance changes alongside large signal-quality changes;
- confidence measures disagree;
- a positive average hides meaningful counterexamples.

### Permitted conclusion

The evidence supports a scoped average effect while preserving participant- and session-level uncertainty.

## Final validated evidence

### Better-supported explanation

Cumulative prior-session decoder adaptation is moderately supported at the studied-sample level. Its benefit is participant- and session-dependent.

### Evidence supporting this explanation

Across seven participants and 35 future-session comparisons:

```text
Mean frozen balanced accuracy:   0.597226
Mean adaptive balanced accuracy: 0.634846
Mean adaptation gain:            +0.037619
Positive session-level gains:    20
Negative session-level gains:    7
Zero session-level gains:        8
Participants improving:          6 of 7
```

### Participant-level evidence

```text
P3: +0.031954
P4: +0.026856
P5: −0.016092
P6: +0.054869
P7: +0.053333
P8: +0.058276
P9: +0.054138
```

### Statistical robustness

```text
Participant-clustered 95% bootstrap interval: [0.017077, 0.052512]
Bootstrap probability mean gain > 0:           0.99975
Participant Wilcoxon p-value:                   0.03125
Participant sign-test p-value:                  0.125
```

The leave-one-participant-out mean gain remained positive for every exclusion.

## Interpretive tension

The participant-clustered bootstrap interval is entirely above zero, the Wilcoxon test supports a positive participant-level shift, and leave-one-participant-out results remain positive.

However:

- the sign test does not reach 0.05;
- one participant has a negative mean gain;
- seven sessions become worse after adaptation;
- eight sessions show zero gain;
- the cumulative decoder receives progressively more training data.

The final interpretation must preserve both the average benefit and the counterevidence.

## Session-shift interpretation

Session-level EEG structure changed across recordings, but the present analysis does not identify the physical or biological cause of that change. Electrode impedance, contact quality, cap-position information, and standardized resting-state measurements are unavailable.

Session shift therefore remains a plausible competing explanation rather than a resolved cause.

## Confidence level

**Moderate** for the conclusion that cumulative prior-session adaptation improves balanced accuracy on average in the studied sample.

**Low or insufficient** for conclusions about:

- universal adaptation benefit;
- population-level generalization;
- neural adaptation;
- neuroplasticity;
- recording-interface causation.

## Final evidence classification

**Adaptation benefit supported at the studied-sample level.**

## Permitted final wording

Across seven participants and 35 future-session comparisons, cumulative prior-session retraining improved balanced accuracy on average relative to a Session-0 frozen decoder. The participant-clustered 95% bootstrap interval for mean gain was entirely above zero, and six of seven participants improved on average. However, negative and zero session-level outcomes occurred, so adaptation should be monitored and selectively applied rather than assumed universally beneficial.

## Claims that must be avoided

Do not state that:

- neuroplasticity was detected;
- a participant's brain rewired;
- adaptation helps every participant or session;
- the result generalizes to the full dataset or population;
- a specific electrode caused the change;
- covariance distance identifies the physical cause of drift;
- NeuroWeave provides a medical diagnosis.

## Bottom line

NeuroWeave separates frozen transfer, cumulative decoder adaptation, participant-aware uncertainty, session-level counterexamples, and unresolved recording drift. The evidence provides moderate support for an average adaptation benefit within the validated P3–P9 sample while showing why adaptation must be monitored instead of enabled blindly.
