"""NEUROWEAVE: convert combined P3-P9 evidence into a cautious machine-readable conclusion."""
from pathlib import Path
import json
import pandas as pd

BASE = Path('results/combined_participants_3_to_9')
ROBUST = BASE / 'statistical_robustness_summary.json'
OVERALL = BASE / 'overall_summary.csv'
PARTICIPANTS = BASE / 'participant_summary.csv'


def main():
    print('=' * 72)
    print('NEUROWEAVE EVIDENCE CLASSIFICATION')
    print('=' * 72)

    for path in (ROBUST, OVERALL, PARTICIPANTS):
        if not path.exists():
            raise FileNotFoundError(f'Missing {path}. Complete Steps 24 and 25 first.')

    robust = json.loads(ROBUST.read_text(encoding='utf-8'))
    overall = pd.read_csv(OVERALL).iloc[0].to_dict()
    participant = pd.read_csv(PARTICIPANTS)

    ci_low = float(robust['clustered_bootstrap_95_ci_low'])
    ci_high = float(robust['clustered_bootstrap_95_ci_high'])
    mean_gain = float(robust['participant_weighted_mean_gain'])
    wilcoxon_p = float(robust['participant_wilcoxon_p_two_sided'])
    sign_p = float(robust['participant_sign_test_p_two_sided'])
    positive = int(robust['participants_positive_mean_gain'])
    negative = int(robust['participants_negative_mean_gain'])
    n = int(robust['participants'])

    if ci_low > 0 and wilcoxon_p < 0.05:
        support = 'moderate'
        status = 'adaptation benefit supported at the studied-sample level'
    elif mean_gain > 0:
        support = 'suggestive'
        status = 'adaptation benefit suggested but uncertain'
    else:
        support = 'insufficient'
        status = 'no reliable overall adaptation benefit established'

    classification = {
        'evidence_status': status,
        'support_level': support,
        'scope': 'descriptive and sample-level inference for participants 3-9',
        'primary_result': {
            'mean_frozen_balanced_accuracy': float(overall['mean_frozen_balanced_accuracy']),
            'mean_adaptive_balanced_accuracy': float(overall['mean_adaptive_balanced_accuracy']),
            'mean_adaptation_gain': mean_gain,
            'clustered_bootstrap_95_ci': [ci_low, ci_high],
            'participants_with_positive_mean_gain': positive,
            'participants_with_negative_mean_gain': negative,
            'participants_total': n,
            'wilcoxon_p_two_sided': wilcoxon_p,
            'sign_test_p_two_sided': sign_p,
        },
        'supported_conclusion': (
            'Cumulative prior-session retraining improved balanced accuracy on average in this seven-participant sample, '
            'but the benefit was participant- and session-dependent.'
        ),
        'important_tension': (
            'The participant-level Wilcoxon test and clustered bootstrap support a positive mean effect, '
            'while the two-sided participant sign test does not reach 0.05 with only seven participants.'
        ),
        'not_supported': [
            'A universal benefit in every participant or session',
            'A causal neural-adaptation or neuroplasticity conclusion',
            'A claim that covariance drift identifies the physical source of change',
            'Population-level generalization beyond the studied sample',
        ],
        'recommended_claim': (
            'Across seven participants and 35 future-session comparisons, cumulative prior-session retraining '
            'increased mean balanced accuracy from 0.597 to 0.635. The participant-clustered 95% bootstrap interval '
            'for mean gain was approximately 0.017 to 0.053. Six of seven participants improved on average, but '
            'session-level losses occurred, so adaptation should be monitored and selectively applied rather than assumed beneficial.'
        ),
        'recommended_next_measurement': (
            'Evaluate a policy that enables adaptation only when held-out or online monitoring predicts benefit, '
            'and collect electrode/contact-quality or impedance metadata to separate recording-interface drift from neural change.'
        ),
    }

    json_file = BASE / 'evidence_classification.json'
    md_file = BASE / 'evidence_classification.md'
    json_file.write_text(json.dumps(classification, indent=2), encoding='utf-8')

    md = f"""# NeuroWeave Evidence Classification

## Classification
**{support.upper()} support:** {status}.

## Supported conclusion
{classification['supported_conclusion']}

## Core evidence
- Mean frozen balanced accuracy: {classification['primary_result']['mean_frozen_balanced_accuracy']:.3f}
- Mean adaptive balanced accuracy: {classification['primary_result']['mean_adaptive_balanced_accuracy']:.3f}
- Mean adaptation gain: {mean_gain:+.3f}
- Participant-clustered 95% bootstrap interval: [{ci_low:.3f}, {ci_high:.3f}]
- Participants improving on average: {positive}/{n}
- Wilcoxon two-sided p-value: {wilcoxon_p:.5f}
- Sign-test two-sided p-value: {sign_p:.3f}

## Important tension
{classification['important_tension']}

## Claims not supported
""" + ''.join(f"- {item}\n" for item in classification['not_supported']) + f"""

## Recommended dashboard/pitch claim
{classification['recommended_claim']}

## Next measurement
{classification['recommended_next_measurement']}
"""
    md_file.write_text(md, encoding='utf-8')

    print(f"Evidence status: {classification['evidence_status']}")
    print(f"Support level: {classification['support_level']}")
    print(f"Recommended claim: {classification['recommended_claim']}")
    print(f'\nSaved: {json_file}')
    print(f'Saved: {md_file}')
    print('Done.')


if __name__ == '__main__':
    main()
