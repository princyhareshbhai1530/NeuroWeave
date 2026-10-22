"""NEUROWEAVE: rebuild the missing P3-P6 session-results CSV from existing arrays."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from pyriemann.estimation import Covariances
from pyriemann.tangentspace import TangentSpace

OUT=Path('outputs'); RES=Path('results'); SUBJECTS=(3,4,5,6)

def model():
    return make_pipeline(Covariances(estimator='oas'),TangentSpace(metric='riemann'),LinearDiscriminantAnalysis(solver='lsqr',shrinkage='auto'))

def score(m,X,y):
    pred=m.predict(X); bal=balanced_accuracy_score(y,pred); f1=f1_score(y,pred,average='weighted')
    try:
        cls=list(m.classes_); pi=cls.index('right_hand') if 'right_hand' in cls else 1
        auc=roc_auc_score((y==cls[pi]).astype(int),m.predict_proba(X)[:,pi])
    except Exception: auc=np.nan
    return bal,f1,auc

def sessions_for(subject,n):
    sf=OUT/f'participant_{subject:02d}_sessions.npy'
    if sf.exists(): return np.load(sf,allow_pickle=True).astype(str)
    # Kumar2024 bar-feedback trial structure used in the established files:
    # S0=80, S1=80, then nominally 60 each; missing trials reduce later counts.
    # We cannot safely infer which later session lost trials, so require stored session metadata.
    raise FileNotFoundError(f'Missing {sf}. Session metadata is required to rebuild P{subject} safely.')

def main():
    print('='*72); print('NEUROWEAVE REBUILD P3-P6 SESSION RESULTS'); print('='*72)
    rows=[]
    for s in SUBJECTS:
        xf=OUT/f'participant_{s:02d}_X.npy'; yf=OUT/f'participant_{s:02d}_y.npy'
        if not xf.exists() or not yf.exists(): raise FileNotFoundError(f'Missing P{s} X/y arrays')
        X=np.load(xf); y=np.load(yf,allow_pickle=True); sess=sessions_for(s,len(y))
        ids=sorted(np.unique(sess).tolist(),key=int)
        print(f'P{s}: X={X.shape} sessions={ids}')
        base=sess==ids[0]; frozen=model().fit(X[base],y[base]); fs={}
        for sid in ids:
            mask=sess==sid; bal,f1,auc=score(frozen,X[mask],y[mask]); fs[sid]=bal
            rows.append(dict(participant=s,session=sid,model='frozen',n_trials=int(mask.sum()),balanced_accuracy=bal,f1=f1,auc=auc,adaptation_gain=np.nan))
        for i,sid in enumerate(ids[1:],1):
            train=np.isin(sess,ids[:i]); test=sess==sid; adaptive=model().fit(X[train],y[train]); bal,f1,auc=score(adaptive,X[test],y[test]); gain=bal-fs[sid]
            rows.append(dict(participant=s,session=sid,model='adaptive',n_trials=int(test.sum()),balanced_accuracy=bal,f1=f1,auc=auc,adaptation_gain=gain))
            print(f'  S{sid}: frozen={fs[sid]:.3f} adaptive={bal:.3f} gain={gain:+.3f}')
    RES.mkdir(exist_ok=True)
    dest=RES/'participants_3_to_6_session_results.csv'; pd.DataFrame(rows).to_csv(dest,index=False)
    print(f'\nSaved: {dest}')
    print('Now rerun: py src/24_combine_participants_3_to_9.py')
if __name__=='__main__': main()
