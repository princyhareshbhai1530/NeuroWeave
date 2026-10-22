"""NEUROWEAVE: participant-aware robustness analysis for P3-P9 adaptation gains."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import binomtest, wilcoxon

INFILE = Path('results/combined_participants_3_to_9/paired_future_session_comparisons.csv')
OUTDIR = Path('results/combined_participants_3_to_9')
SEED = 20261021
N_BOOT = 20000


def clustered_bootstrap(df, rng):
    participants = np.array(sorted(df['participant'].unique()))
    means = np.empty(N_BOOT)
    for b in range(N_BOOT):
        sampled = rng.choice(participants, size=len(participants), replace=True)
        chunks = [df[df['participant'] == p]['adaptation_gain'].to_numpy() for p in sampled]
        means[b] = np.concatenate(chunks).mean()
    return means


def main():
    print('=' * 72)
    print('NEUROWEAVE STATISTICAL ROBUSTNESS: PARTICIPANTS 3 TO 9')
    print('=' * 72)
    if not INFILE.exists():
        raise FileNotFoundError(f'Missing {INFILE}. Run Step 24 first.')

    df = pd.read_csv(INFILE)
    required = {'participant', 'session', 'adaptation_gain'}
    if not required.issubset(df.columns):
        raise ValueError(f'Missing columns: {sorted(required - set(df.columns))}')

    participant = df.groupby('participant', as_index=False)['adaptation_gain'].mean()
    gains = participant['adaptation_gain'].to_numpy()
    rng = np.random.default_rng(SEED)
    boot = clustered_bootstrap(df, rng)
    ci_low, ci_high = np.quantile(boot, [0.025, 0.975])
    probability_positive = float((boot > 0).mean())

    nonzero = gains[np.abs(gains) > 1e-12]
    sign = binomtest(int((nonzero > 0).sum()), n=len(nonzero), p=0.5, alternative='two-sided')
    try:
        w = wilcoxon(gains, alternative='two-sided', zero_method='wilcox', method='auto')
        wilcoxon_stat, wilcoxon_p = float(w.statistic), float(w.pvalue)
    except ValueError:
        wilcoxon_stat, wilcoxon_p = np.nan, np.nan

    loo = []
    for excluded in sorted(df['participant'].unique()):
        subset = df[df['participant'] != excluded]
        loo.append({'excluded_participant': int(excluded),
                    'remaining_mean_gain': float(subset['adaptation_gain'].mean())})
    loo_df = pd.DataFrame(loo)

    summary = {
        'participants': int(df['participant'].nunique()),
        'future_session_comparisons': int(len(df)),
        'session_weighted_mean_gain': float(df['adaptation_gain'].mean()),
        'participant_weighted_mean_gain': float(gains.mean()),
        'participant_median_gain': float(np.median(gains)),
        'clustered_bootstrap_95_ci_low': float(ci_low),
        'clustered_bootstrap_95_ci_high': float(ci_high),
        'clustered_bootstrap_probability_mean_gain_positive': probability_positive,
        'participants_positive_mean_gain': int((gains > 1e-12).sum()),
        'participants_negative_mean_gain': int((gains < -1e-12).sum()),
        'participants_zero_mean_gain': int((np.abs(gains) <= 1e-12).sum()),
        'participant_sign_test_p_two_sided': float(sign.pvalue),
        'participant_wilcoxon_statistic': wilcoxon_stat,
        'participant_wilcoxon_p_two_sided': wilcoxon_p,
        'bootstrap_iterations': N_BOOT,
        'random_seed': SEED,
    }

    participant.to_csv(OUTDIR / 'participant_mean_gains_for_inference.csv', index=False)
    loo_df.to_csv(OUTDIR / 'leave_one_participant_out.csv', index=False)
    (OUTDIR / 'statistical_robustness_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')

    print('\nPARTICIPANT MEAN GAINS')
    print(participant.to_string(index=False))
    print('\nROBUSTNESS SUMMARY')
    for key, value in summary.items():
        print(f'{key}: {value}')
    print('\nLEAVE-ONE-PARTICIPANT-OUT')
    print(loo_df.to_string(index=False))
    print('\nINTERPRETATION RULE')
    if ci_low > 0:
        print('The clustered bootstrap interval is entirely above zero.')
    elif ci_high < 0:
        print('The clustered bootstrap interval is entirely below zero.')
    else:
        print('The clustered bootstrap interval includes zero; evidence is suggestive, not conclusive.')
    print('Do not interpret this analysis as evidence of neuroplasticity or causation.')
    print(f'\nSaved robustness outputs to: {OUTDIR}')


if __name__ == '__main__':
    main()
