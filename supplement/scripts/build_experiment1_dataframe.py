#!/usr/bin/env python3
"""Build the dataframe consumed by the Experiment 1 analysis notebooks."""
from pathlib import Path
import argparse
from polygraphs.analysis import Processor

p = argparse.ArgumentParser()
p.add_argument('results', help='Directory containing regenerated Experiment 1 PolyGraphs runs')
p.add_argument('--output', default='supplement/analysis/experiment_1/raw_data/bigsimpleframe.csv')
a = p.parse_args()
proc = Processor(a.results, config_check=False)
if proc.sims.empty:
    raise ValueError('No complete simulation results found in the supplied directory.')
proc.add_config(
    'reliability',
    'network.barabasialbert.attachments',
    'network.wattsstrogatz.knn',
    'network.wattsstrogatz.probability',
    'network.random.probability',
    'simulation.steps',
)
out = Path(a.output)
out.parent.mkdir(parents=True, exist_ok=True)
proc.sims.to_csv(out)
print(f'Wrote {len(proc.sims)} runs to {out}')
