# NeuroWeave Evidence Classification

## Classification
**MODERATE support:** adaptation benefit supported at the studied-sample level.

## Supported conclusion
Cumulative prior-session retraining improved balanced accuracy on average in this seven-participant sample, but the benefit was participant- and session-dependent.

## Core evidence
- Mean frozen balanced accuracy: 0.597
- Mean adaptive balanced accuracy: 0.635
- Mean adaptation gain: +0.038
- Participant-clustered 95% bootstrap interval: [0.017, 0.053]
- Participants improving on average: 6/7
- Wilcoxon two-sided p-value: 0.03125
- Sign-test two-sided p-value: 0.125

## Important tension
The participant-level Wilcoxon test and clustered bootstrap support a positive mean effect, while the two-sided participant sign test does not reach 0.05 with only seven participants.

## Claims not supported
- A universal benefit in every participant or session
- A causal neural-adaptation or neuroplasticity conclusion
- A claim that covariance drift identifies the physical source of change
- Population-level generalization beyond the studied sample


## Recommended dashboard/pitch claim
Across seven participants and 35 future-session comparisons, cumulative prior-session retraining increased mean balanced accuracy from 0.597 to 0.635. The participant-clustered 95% bootstrap interval for mean gain was approximately 0.017 to 0.053. Six of seven participants improved on average, but session-level losses occurred, so adaptation should be monitored and selectively applied rather than assumed beneficial.

## Next measurement
Evaluate a policy that enables adaptation only when held-out or online monitoring predicts benefit, and collect electrode/contact-quality or impedance metadata to separate recording-interface drift from neural change.
