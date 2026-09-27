#!/usr/bin/env python3
"""Fresh Experiment 1 summaries and count-based comparisons, not historical p-values."""
import argparse
from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu

KEYS = ['network_size', 'op', 'reliability', 'network_barabasialbert_attachments']

def analyse(df):
    df = df[(df.network_kind == 'barabasialbert') & (df.trials == 64) & np.isclose(df.epsilon, 0.001)].copy()
    main = df.network_size == 64
    subset = (df.network_size == 32) & (df.op == 'UnreliableNetworkBasicGullibleBinomialOp') & (df.reliability == 0.25)
    df = df[main | subset]
    if df.empty:
        raise ValueError('No Experiment 1 paper conditions found.')
    if not df.action.isin(['A','B','?']).all() or df.steps.isna().any():
        raise ValueError('Missing or invalid simulation outcomes.')
    rows=[];groups={}
    for key,g in df.groupby(KEYS,observed=True):
        groups[key]=g
        a=int((g.action=='A').sum());b=int((g.action=='B').sum())
        successful=g.loc[g.action=='B','steps']
        rows.append(dict(zip(KEYS,key),n_runs=len(g),n_A=a,n_B=b,n_unconverged=len(g)-a-b,
            accuracy_given_convergence=b/(a+b) if a+b else np.nan,
            mean_steps_to_B=successful.mean(),median_steps_to_B=successful.median()))
    tests=[]
    for k1,k2 in combinations(groups,2):
        if k1[0] != k2[0]:continue
        differences=[i for i in range(1,4) if k1[i]!=k2[i]]
        baseline=(k1[1]=='BalaGoyalOp' or k2[1]=='BalaGoyalOp') and k1[3]==k2[3]
        if len(differences)!=1 and not baseline:continue
        g1,g2=groups[k1],groups[k2]
        table=np.array([[(g.action=='A').sum(),(g.action=='B').sum()] for g in (g1,g2)],dtype=int)
        row={'group_1':str(k1),'group_2':str(k2),'comparison':'baseline' if baseline else KEYS[differences[0]],
             'chi2_p':np.nan,'fisher_p':np.nan,'min_expected_count':np.nan,'mann_whitney_p':np.nan,
             'accuracy_status':'no converged observations in at least one group'}
        if (table.sum(axis=1)>0).all():
            row['fisher_p']=fisher_exact(table).pvalue
            if (table.sum(axis=0)>0).all():
                result=chi2_contingency(table) # Matches historical default Yates correction for 2x2 tables.
                row['chi2_p']=result.pvalue;row['min_expected_count']=result.expected_freq.min()
                row['accuracy_status']='sparse: prefer Fisher exact' if result.expected_freq.min()<5 else 'ok'
            else:row['accuracy_status']='no outcome variation; chi-squared undefined'
        x=g1.loc[g1.action=='B','steps'];y=g2.loc[g2.action=='B','steps']
        if len(x) and len(y):row['mann_whitney_p']=mannwhitneyu(x,y,alternative='two-sided').pvalue
        tests.append(row)
    return pd.DataFrame(rows),pd.DataFrame(tests)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv');p.add_argument('--output',default='supplement/analysis/experiment_1/results')
    a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    summary,tests=analyse(pd.read_csv(a.csv))
    summary.to_csv(out/'summary.csv',index=False);tests.to_csv(out/'comparisons.csv',index=False)
    print(f'Wrote {len(summary)} condition summaries and {len(tests)} comparisons. P-values are unadjusted fresh analyses.')
if __name__=='__main__':main()
