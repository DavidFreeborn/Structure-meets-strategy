#!/usr/bin/env python3
"""Build Experiment 2 outcomes and structural predictors for the main four conditions."""
from pathlib import Path
import argparse
from polygraphs.analysis import Processor
import networkx as nx

OPS = [
    'UnreliableNetworkBasicGullibleBinomialOp',
    'UnreliableNetworkModifiedAlignedBinomialOp',
    'UnreliableNetworkBasicGullibleNegativeEpsOp',
    'UnreliableNetworkModifiedAlignedNegativeEpsOp',
]

def environment(op):
    return 'disinfo' if 'NegativeEps' in op else 'misinfo'

def strategy(op):
    return 'gullible' if 'Gullible' in op else 'aligned'

p = argparse.ArgumentParser()
p.add_argument('results', help='Directory containing regenerated Experiment 2 PolyGraphs runs')
p.add_argument('--output', default='supplement/analysis/experiment_2/raw_data/main_factorial.csv')
a = p.parse_args()
proc = Processor(a.results, config_check=False)
if proc.sims.empty:
    raise ValueError('No complete simulation results found in the supplied directory.')
proc.add_config('reliability')
df = proc.sims.copy()
df = df[
    (df.network_size == 64)
    & (df.epsilon == 0.001)
    & (df.op.astype(str).isin(OPS))
    & (df.reliability == 0.75)
].copy()
df['environment'] = df.op.astype(str).map(environment)
df['strategy'] = df.op.astype(str).map(strategy)
if df.empty:
    raise ValueError('No main factorial conditions found.')
for idx in df.index:
    graph = proc.graphs[int(idx)]
    if not nx.is_connected(graph):
        raise ValueError('Experiment 2 requires connected graphs.')
    df.loc[idx, 'density'] = nx.density(graph)
    df.loc[idx, 'clustering'] = nx.average_clustering(graph)
    df.loc[idx, 'path_length'] = nx.average_shortest_path_length(graph)
    df.loc[idx, 'reliable_node_count'] = int(graph.pg['ndata']['reliability'].sum().item())
out = Path(a.output)
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)
print(f'Wrote {len(df)} runs to {out}')
