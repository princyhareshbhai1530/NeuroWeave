"""NEUROWEAVE: safely restore P3-P6 session metadata by re-running established MOABB preprocessing, verify exact X/y equality, then rebuild results."""
from pathlib import Path
import numpy as np
import pandas as pd
from moabb.datasets import Kumar2024
from moabb.paradigms import MotorImagery
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from pyriemann.estimation import Covariances
from pyriemann.tangentspace import TangentSpace

OUT=Path('outputs'); RES=Path('results'); SUBJECTS=(3,4,5,6)
paradigm=MotorImagery(fmin=8,fmax=30,tmin=0.0,tmax=5.0,resample=128)

def decoder():
    return make_pipeline(Covariances(estimator='oas'),TangentSpace(metric='riemann'),LinearDiscriminantAnalysis(solver='lsqr',shrinkage='auto'))

def score(m,X,y):
    pred=m.predict(X); bal=balanced_accuracy_score(y,pred); f1=f1_score(y,pred,average='weighted')
    cls=list(m.classes_); pi=cls.index('right_hand') if 'right_hand' in cls else 1
    auc=roc_auc_score((y==cls[pi]).astype(int),m.predict_proba(X)[:,pi])
    return bal,f1,auc

def main():
    print('='*72); print('NEUROWEAVE SAFE RESTORE: P3-P6'); print('='*72)
    dataset=Kumar2024(); rows=[]
    for s in SUBJECTS:
        print('\n'+'='*72); print(f'RESTORING PARTICIPANT {s}'); print('='*72)
        xf=OUT/f'participant_{s:02d}_X.npy'; yf=OUT/f'participant_{s:02d}_y.npy'
        if not xf.exists() or not yf.exists(): raise FileNotFoundError(f'Missing original P{s} arrays')
        oldX=np.load(xf); oldy=np.load(yf,allow_pickle=True)
        newX,newy,meta=paradigm.get_data(dataset=dataset,subjects=[s]); sessions=meta['session'].astype(str).to_numpy()
        print(f'old X: {oldX.shape} | regenerated X: {newX.shape}')
        if oldX.shape!=newX.shape or not np.array_equal(oldy,newy):
            raise RuntimeError(f'P{s}: regenerated data ordering does not match saved arrays; refusing to attach session metadata.')
        maxdiff=float(np.max(np.abs(oldX-newX)))
        print(f'max |oldX-newX| = {maxdiff:.3e}')
        if not np.allclose(oldX,newX,rtol=1e-7,atol=1e-10,equal_nan=True):
            raise RuntimeError(f'P{s}: regenerated EEG values differ from saved arrays; refusing unsafe reconstruction.')
        sf=OUT/f'participant_{s:02d}_sessions.npy'; np.save(sf,sessions); print(f'Saved verified sessions: {sf}')
        ids=sorted(np.unique(sessions).tolist(),key=int); base=sessions==ids[0]
        frozen=decoder().fit(oldX[base],oldy[base]); frozen_scores={}
        for sid in ids:
            mask=sessions==sid; bal,f1,auc=score(frozen,oldX[mask],oldy[mask]); frozen_scores[sid]=bal
            rows.append(dict(participant=s,session=sid,model='frozen',n_trials=int(mask.sum()),balanced_accuracy=bal,f1=f1,auc=auc,adaptation_gain=np.nan))
        for i,sid in enumerate(ids[1:],1):
            train=np.isin(sessions,ids[:i]); test=sessions==sid; adaptive=decoder().fit(oldX[train],oldy[train]); bal,f1,auc=score(adaptive,oldX[test],oldy[test]); gain=bal-frozen_scores[sid]
            rows.append(dict(participant=s,session=sid,model='adaptive',n_trials=int(test.sum()),balanced_accuracy=bal,f1=f1,auc=auc,adaptation_gain=gain))
            print(f'S{sid}: frozen={frozen_scores[sid]:.3f} adaptive={bal:.3f} gain={gain:+.3f}')
    RES.mkdir(exist_ok=True); dest=RES/'participants_3_to_6_session_results.csv'; pd.DataFrame(rows).to_csv(dest,index=False)
    print(f'\nSaved: {dest}'); print('NEXT: py src/24_combine_participants_3_to_9.py')
if __name__=='__main__': main()
