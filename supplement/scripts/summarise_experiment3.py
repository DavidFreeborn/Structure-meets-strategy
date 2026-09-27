#!/usr/bin/env python3
"""Summarise one network: pooled mean/25th percentile and mean within-run SD (ddof=1).

Processes one condition and recorded iteration at a time to limit memory use.
Terminated simulations are not carried forward. Output records contributing runs.
"""
import argparse
from pathlib import Path
import dgl
import h5py
import numpy as np
import pandas as pd
from polygraphs.analysis import Processor

def summarise_arrays(arrays):
    pooled=np.concatenate(arrays)
    return dict(mean_credence=float(pooled.mean()), p25_credence=float(np.quantile(pooled,0.25)),
                mean_within_sim_sd=float(np.mean([v.std(ddof=1) for v in arrays])))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('results');p.add_argument('--output',required=True)
    a=p.parse_args();processor=Processor(a.results,config_check=False);processor.add_config('reliability','network.gml.name')
    df=processor.sims
    if df.empty:raise ValueError('No complete simulation results found.')
    if df.network_gml_name.nunique(dropna=False)!=1:raise ValueError('Supply results for exactly one empirical network.')
    rows=[]
    for (op,r),group in df.groupby(['op','reliability'],observed=True):
        runs=[];iterations={0}
        for sim in group.itertuples():
            graph=dgl.load_graphs(sim.bin_file_path)[0][0]
            initial=graph.ndata['beliefs'].cpu().numpy().astype('float64')
            with h5py.File(sim.hd5_file_path,'r') as f:keys=set(map(int,f['beliefs'].keys()))
            iterations.update(keys);runs.append((sim.hd5_file_path,initial,keys))
        for step in sorted(iterations):
            arrays=[]
            for path,initial,keys in runs:
                if step==0:values=initial
                elif step in keys:
                    with h5py.File(path,'r') as f:values=np.asarray(f['beliefs'][str(step)],dtype='float64').reshape(-1)
                else:continue
                if not np.isfinite(values).all():raise ValueError(f'Nonfinite credences: {path}, iteration {step}')
                arrays.append(values)
            pooled=np.concatenate(arrays)
            rows.append(dict(op=str(op),reliability=float(r),iteration=step,n_simulations=len(arrays),n_agents_pooled=len(pooled),
                **summarise_arrays(arrays)))
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out,index=False);print(f'Wrote {len(rows)} condition/iteration summaries to {out}')
if __name__=='__main__':main()
