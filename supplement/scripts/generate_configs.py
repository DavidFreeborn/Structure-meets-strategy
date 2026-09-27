#!/usr/bin/env python3
"""Expand compact SMS specifications into runnable PolyGraphs YAML files.

Run this from the repository root. Generated files are intentionally ignored by Git.
"""
from pathlib import Path
import copy, yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / 'configs'
OUT = CFG / 'generated'
OUT.mkdir(exist_ok=True)
# This directory contains only generated files. Remove stale generated configs.
for stale in OUT.glob('e*.yaml'):
    stale.unlink()
common = yaml.safe_load((CFG / 'common.yaml').read_text())

def base(results):
    config = {
        'device': common['device'], 'seed': common['seed'], 'epsilon': common['epsilon'],
        'trials': common['trials'], 'lowerupper': common['lowerupper'], 'upperlower': common['upperlower'],
        'mistrust': common['mistrust'], 'antiupdating': common['antiupdating'], 'trust': common['trust'],
        'unreliablenodes': copy.deepcopy(common['unreliablenodes']), 'init': copy.deepcopy(common['init']),
        'logging': copy.deepcopy(common['logging']), 'snapshots': copy.deepcopy(common['snapshots']),
        'network': {
            'kind': None, 'size': None, 'directed': common['network_defaults']['directed'], 'selfloop': common['network_defaults']['selfloop'],
            'random': {'seed': None, 'tries': 100, 'probability': 1.0},
            'wattsstrogatz': {'knn': 2, 'seed': None, 'tries': 100, 'probability': 1.0},
            'barabasialbert': {'attachments': 1, 'seed': None},
            'snap': {'name': None}, 'ogb': {'name': 'collab'},
            'gml': {'name': None, 'path': None, 'directed': False},
        },
        'simulation': {'results': results, 'repeats': 100, 'steps': 100000},
    }

    for family in ('random', 'wattsstrogatz', 'barabasialbert'):
        config['network'][family].update(common['network_defaults'][family])
    return config

def dump(c, name):
    (OUT / name).write_text(yaml.safe_dump(c, sort_keys=False))

# Experiment 1 main
s = yaml.safe_load((CFG / 'experiment_1.yaml').read_text())
for cond in s['conditions']:
    for r in cond['reliability']:
        for m in s['network']['attachments']:
            c = base('supplement/outputs/experiment_1/auto')
            c['op'], c['reliability'] = cond['op'], r
            c['network']['kind'], c['network']['size'] = 'barabasialbert', s['network']['size']
            c['network']['barabasialbert']['attachments'] = m
            c['simulation']['steps'], c['simulation']['repeats'] = s['simulation']['steps'], s['simulation']['repeats']
            dump(c, f"e1_{cond['op']}_r{r}_m{m}.yaml")

# Experiment 1 Zollman subset
z = yaml.safe_load((CFG / 'experiment_1_zollman.yaml').read_text())
for m, n in z['historical_analysis_counts'].items():
    c = base('supplement/outputs/experiment_1/auto')
    c['op'], c['reliability'] = z['condition']['op'], z['condition']['reliability']
    c['network']['kind'], c['network']['size'] = 'barabasialbert', z['network']['size']
    c['network']['barabasialbert']['attachments'] = int(m)
    c['simulation']['steps'], c['simulation']['repeats'] = z['simulation']['steps'], int(n)
    dump(c, f'e1_zollman_m{m}.yaml')

# Experiment 2
s = yaml.safe_load((CFG / 'experiment_2.yaml').read_text())
for cond in s['conditions']:
    for p in s['network_families']['random']['probability']:
        c = base('supplement/outputs/experiment_2/auto')
        c['op'], c['reliability'] = cond['op'], cond['reliability']
        c['network']['kind'], c['network']['size'] = 'random', s['network_size']
        c['network']['random']['probability'] = p
        c['network']['random']['tries'] = s['network_families']['random']['tries']
        c['simulation'].update({key: s['simulation'][key] for key in ('repeats', 'steps')})
        dump(c, f"e2_{cond['op']}_er_p{p}.yaml")
    for k in s['network_families']['wattsstrogatz']['knn']:
        for p in s['network_families']['wattsstrogatz']['probability']:
            c = base('supplement/outputs/experiment_2/auto')
            c['op'], c['reliability'] = cond['op'], cond['reliability']
            c['network']['kind'], c['network']['size'] = 'wattsstrogatz', s['network_size']
            c['network']['wattsstrogatz']['knn'] = k
            c['network']['wattsstrogatz']['probability'] = p
            c['network']['wattsstrogatz']['tries'] = s['network_families']['wattsstrogatz']['tries']
            c['simulation'].update({key: s['simulation'][key] for key in ('repeats', 'steps')})
            dump(c, f"e2_{cond['op']}_ws_k{k}_p{p}.yaml")
    for m in s['network_families']['barabasialbert']['attachments']:
        c = base('supplement/outputs/experiment_2/auto')
        c['op'], c['reliability'] = cond['op'], cond['reliability']
        c['network']['kind'], c['network']['size'] = 'barabasialbert', s['network_size']
        c['network']['barabasialbert']['attachments'] = m
        c['simulation'].update({key: s['simulation'][key] for key in ('repeats', 'steps')})
        dump(c, f"e2_{cond['op']}_ba_m{m}.yaml")

# Experiment 3
s = yaml.safe_load((CFG / 'experiment_3.yaml').read_text())
for name, net in s['networks'].items():
    for cond in s['conditions']:
        c = base(f'supplement/outputs/experiment_3/{name}/auto')
        c['op'], c['reliability'] = cond['op'], cond['reliability']
        c['network']['kind'], c['network']['size'] = 'gml', net['nodes']
        c['network']['gml']['name'] = name
        c['network']['gml']['path'] = net['path']
        c['network']['gml']['directed'] = False
        c['simulation']['steps'], c['simulation']['repeats'] = s['simulation']['steps'], net['repeats']
        c['snapshots']['interval'] = s['simulation']['snapshot_interval']
        dump(c, f"e3_{name}_{cond['op']}.yaml")

print(f'Wrote {len(list(OUT.glob("*.yaml")))} configs to {OUT}')
