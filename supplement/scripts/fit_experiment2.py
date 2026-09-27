#!/usr/bin/env python3
"""Fit the documented final model specifications on fresh Experiment 2 data.

This is fixed-specification replication, not a repeat of model selection.
See the multivariate notebook for historical selection and robustness checks.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
BASE='C(environment) + C(strategy) + C(network_kind) + density_z + clustering_z + path_length_z + reliable_node_count_z'
STRUCT='density_z:clustering_z + density_z:path_length_z + path_length_z:clustering_z'
ACC='outcome ~ '+BASE+' + '+STRUCT+' + '+ ' + '.join(f'C({c}):{x}_z' for c in ['environment','strategy'] for x in ['density','clustering','path_length','reliable_node_count'])
EFF='steps_to_B ~ '+BASE+' + '+STRUCT+' + C(environment):C(strategy) + C(environment):reliable_node_count_z'

def fit_models(df):
    df=df.copy()
    for col,levels in [('environment',['disinfo','misinfo']),('strategy',['aligned','gullible']),('network_kind',['barabasialbert','random','wattsstrogatz'])]:
        if not df[col].isin(levels).all():raise ValueError(f'Unexpected {col} values')
        df[col]=pd.Categorical(df[col],categories=levels)
    df['outcome']=((df.action=='B') & (df.steps<=100000)).astype(int)
    if df.outcome.nunique()!=2:raise ValueError('Accuracy fitting requires both successes and failures.')
    scaling={}
    for col in ['density','clustering','path_length','reliable_node_count']:
        mean=float(df[col].mean());sd=float(df[col].std(ddof=1))
        if not np.isfinite(sd) or sd<=0:raise ValueError(f'No usable variation in {col}')
        scaling[col]={'mean':mean,'sd':sd};df[col+'_z']=(df[col]-mean)/sd
    successful=df[df.outcome==1].rename(columns={'steps':'steps_to_B'})
    models={'accuracy':smf.logit(ACC,df).fit(disp=False,maxiter=200),
            'efficiency':smf.negativebinomial(EFF,successful).fit(disp=False,maxiter=200)}
    return models,scaling

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv');p.add_argument('--output',default='supplement/analysis/experiment_2/results/main-analysis');a=p.parse_args()
    models,scaling=fit_models(pd.read_csv(a.csv));out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    diagnostics={};failed=[]
    for name,m in models.items():
        ci=m.conf_int();pd.DataFrame({'coef':m.params,'std_error':m.bse,'ci_low':ci[0],'ci_high':ci[1],'p_value':m.pvalues}).to_csv(out/f'{name}_model_results.csv',index_label='term')
        (out/f'{name}_summary.txt').write_text(str(m.summary()))
        ok=bool(m.mle_retvals.get('converged',False)) and np.isfinite(m.params).all() and np.isfinite(m.bse).all()
        diagnostics[name]={'formula':m.model.formula,'n':int(m.nobs),'converged_finite':bool(ok),'aic':float(m.aic),'bic':float(m.bic),'pseudo_r2':float(m.prsquared)}
        if not ok:failed.append(name)
    (out/'diagnostics.json').write_text(json.dumps({'scaling_full_accuracy_sample':scaling,'models':diagnostics},indent=2))
    if failed:raise RuntimeError('Unusable model fit(s): '+', '.join(failed)+'. Inspect saved diagnostics; no inference is certified.')
    print('Fits completed. Inspect warnings, standard errors and separation before interpretation.')
if __name__=='__main__':main()
