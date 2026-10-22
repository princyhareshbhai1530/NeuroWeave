"""NEUROWEAVE: combine validated results for participants 3-9."""
from pathlib import Path
import pandas as pd
import numpy as np

RESULTS = Path('results')
OUT = RESULTS / 'combined_participants_3_to_9'


def locate(required_terms, exclude_terms=()):
    matches=[]
    for p in RESULTS.glob('*.csv'):
        n=p.name.lower()
        if all(t in n for t in required_terms) and not any(t in n for t in exclude_terms):
            matches.append(p)
    return sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True)


def standardize(df, source):
    aliases={
        'subject':'participant', 'participant_id':'participant',
        'balanced_acc':'balanced_accuracy', 'balanced accuracy':'balanced_accuracy',
        'adaptation gain':'adaptation_gain'
    }
    df=df.rename(columns={c:aliases.get(c.lower(),c) for c in df.columns})
    needed={'participant','session','model','balanced_accuracy'}
    missing=needed-set(df.columns)
    if missing:
        raise ValueError(f'{source} is missing columns: {sorted(missing)}; found {list(df.columns)}')
    df['participant']=pd.to_numeric(df['participant'], errors='raise').astype(int)
    df['session']=df['session'].astype(str)
    df['model']=df['model'].astype(str).str.lower()
    df['balanced_accuracy']=pd.to_numeric(df['balanced_accuracy'], errors='coerce')
    if 'adaptation_gain' not in df.columns:
        df['adaptation_gain']=np.nan
    df['source_file']=source.name
    return df


def main():
    print('='*72)
    print('NEUROWEAVE COMBINED PARTICIPANTS 3 TO 9')
    print('='*72)
    OUT.mkdir(parents=True, exist_ok=True)

    old=locate(('3','6','session'), ('7_to_9',))
    exact=RESULTS/'participants_7_to_9_exact_session_results.csv'
    if not old:
        print('Could not automatically find the P3-P6 session-results CSV.')
        print('CSV files currently in results/:')
        for p in RESULTS.glob('*.csv'): print(' -',p)
        raise FileNotFoundError('Expected a P3-P6 session-results CSV in results/.')
    if not exact.exists():
        raise FileNotFoundError(f'Missing {exact}; run Step 23 first.')

    old_file=old[0]
    print(f'Using P3-P6: {old_file}')
    print(f'Using P7-P9: {exact}')
    combined=pd.concat([
        standardize(pd.read_csv(old_file), old_file),
        standardize(pd.read_csv(exact), exact)
    ], ignore_index=True)
    combined=combined[combined['participant'].between(3,9)].copy()

    future=combined[combined['session']!='0'].copy()
    frozen=future[future['model']=='frozen'][['participant','session','balanced_accuracy']].rename(columns={'balanced_accuracy':'frozen_balanced_accuracy'})
    adaptive=future[future['model']=='adaptive'][['participant','session','balanced_accuracy']].rename(columns={'balanced_accuracy':'adaptive_balanced_accuracy'})
    paired=frozen.merge(adaptive,on=['participant','session'],how='inner')
    paired['adaptation_gain']=paired['adaptive_balanced_accuracy']-paired['frozen_balanced_accuracy']

    participant_summary=paired.groupby('participant').agg(
        comparisons=('adaptation_gain','size'),
        mean_frozen=('frozen_balanced_accuracy','mean'),
        mean_adaptive=('adaptive_balanced_accuracy','mean'),
        mean_gain=('adaptation_gain','mean'),
        positive_gains=('adaptation_gain',lambda x:int((x>1e-12).sum())),
        negative_gains=('adaptation_gain',lambda x:int((x<-1e-12).sum())),
        zero_gains=('adaptation_gain',lambda x:int((x.abs()<=1e-12).sum()))
    ).reset_index()

    overall=pd.DataFrame([{
        'participants': paired['participant'].nunique(),
        'future_session_comparisons': len(paired),
        'mean_frozen_balanced_accuracy': paired['frozen_balanced_accuracy'].mean(),
        'mean_adaptive_balanced_accuracy': paired['adaptive_balanced_accuracy'].mean(),
        'mean_adaptation_gain': paired['adaptation_gain'].mean(),
        'positive_gains': int((paired['adaptation_gain']>1e-12).sum()),
        'negative_gains': int((paired['adaptation_gain']<-1e-12).sum()),
        'zero_gains': int((paired['adaptation_gain'].abs()<=1e-12).sum()),
    }])

    combined.to_csv(OUT/'combined_session_results.csv',index=False)
    paired.to_csv(OUT/'paired_future_session_comparisons.csv',index=False)
    participant_summary.to_csv(OUT/'participant_summary.csv',index=False)
    overall.to_csv(OUT/'overall_summary.csv',index=False)

    print('\nOVERALL FUTURE-SESSION SUMMARY')
    print(overall.to_string(index=False))
    print('\nPARTICIPANT SUMMARY')
    print(participant_summary.to_string(index=False))
    print(f'\nSaved combined outputs to: {OUT}')
    print('CAUTION: descriptive aggregation only; it does not establish neuroplasticity or causation.')


if __name__=='__main__':
    main()
