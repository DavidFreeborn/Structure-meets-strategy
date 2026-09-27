#!/usr/bin/env python3
"""Validate the packaged files and pinned PolyGraphs schema. Nonzero exit on failure."""
import argparse,ast,hashlib,json,subprocess,sys
from pathlib import Path
import networkx as nx
import yaml
import nbformat
ROOT=Path(__file__).resolve().parents[1]
def require(condition,message):
    if not condition:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--static-only',action='store_true',help='Explicitly skip installed-environment checks; not a release check')
    p.add_argument('--require-all-networks',action='store_true');a=p.parse_args()
    manifest=json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())
    for path in ROOT.rglob('*.ipynb'):
        nb=json.loads(path.read_text(encoding='utf-8'));nbformat.validate(nb);require(nb.get('nbformat')==4,f'Invalid notebook: {path}')
        for cell in nb['cells']:
            if cell['cell_type']=='code':
                require(not cell.get('outputs') and cell.get('execution_count') is None,f'Embedded output: {path}')
                if '/analysis/' in str(path):ast.parse(''.join(cell['source']))
    for path in (ROOT/'scripts').glob('*.py'):ast.parse(path.read_text())
    for key,info in manifest['networks'].items():
        path=ROOT.parent/info['file']
        if not path.exists():
            require(key=='francis_bacon' and not a.require_all_networks,f'Missing network: {path}')
            print('INCOMPLETE DATA: empirical snapshot absent; its Experiment 3 conditions cannot run.');continue
        require(sha(path)==info['sha256'],f'Network file checksum mismatch: {key}')
        g=nx.read_gml(path,destringizer=int)
        require((len(g),g.number_of_edges())==(info['nodes'],info['edges']),f'Network dimensions: {key}')
        require(not g.is_directed() and nx.is_connected(g) and nx.number_of_selfloops(g)==0,f'Unexpected topology: {key}')
        payload=''.join(f'{u} {v}\n' for u,v in sorted((min(int(u),int(v)),max(int(u),int(v))) for u,v in g.edges())).encode()
        require(hashlib.sha256(payload).hexdigest()==info['topology_sha256'],f'Network topology checksum mismatch: {key}')
    subprocess.run([sys.executable,str(ROOT/'scripts/generate_configs.py')],check=True)
    paths=sorted((ROOT/'configs/generated').glob('*.yaml'))
    require(len(paths)==341,'Expected 341 configurations')
    require([sum(x.name.startswith(prefix) for x in paths) for prefix in ('e1_','e2_','e3_')]==[83,246,12],'Experiment configuration counts')
    for path in paths:
        cfg=yaml.safe_load(path.read_text());require(cfg['simulation']['steps'] in (25000,100000),'Horizon mismatch')
        require(cfg['epsilon']==0.001 and cfg['trials']==64,'Evidence parameters')
        require(set(cfg['simulation'])=={'results','repeats','steps'},'Unsupported simulation settings')
    if not a.static_only:
        from polygraphs.hyperparameters import PolyGraphHyperParameters
        from polygraphs import ops
        import torch,dgl,torchdata
        for path in paths:
            h=PolyGraphHyperParameters.load([str(path)]);ops.getbyname(h.op)
        print(f'Installed environment: Torch {torch.__version__}; DGL {dgl.__version__}; TorchData {torchdata.__version__}')
        print('Package and PolyGraphs schema checks passed. This is not a full numerical replication.')
    else:print('Static checks passed ONLY. Installed-environment and execution checks were explicitly skipped.')
if __name__=='__main__':main()
