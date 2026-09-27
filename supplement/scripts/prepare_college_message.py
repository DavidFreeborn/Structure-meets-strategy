#!/usr/bin/env python3
"""Reconstruct the Experiment 3 College Message topology from SNAP."""
from pathlib import Path
import argparse, gzip, tempfile, urllib.request, hashlib, json
import networkx as nx
URL = 'https://snap.stanford.edu/data/CollegeMsg.txt.gz'

def build(stream):
    G = nx.Graph()
    for line in stream:
        if not line.strip() or line.startswith('#'):
            continue
        u, v, *_ = map(int, line.split())
        G.add_edge(u, v)
    G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
    return nx.relabel_nodes(G, {n:i for i,n in enumerate(sorted(G.nodes()))}, copy=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', help='Optional local CollegeMsg.txt or CollegeMsg.txt.gz')
    p.add_argument('--output', default='supplement/networks/college_message.gml')
    a = p.parse_args()
    if a.input:
        opener = gzip.open if str(a.input).endswith('.gz') else open
        with opener(a.input, 'rt') as f:
            G = build(f)
    else:
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / 'CollegeMsg.txt.gz'
            urllib.request.urlretrieve(URL, raw)
            with gzip.open(raw, 'rt') as f:
                G = build(f)
    if (G.number_of_nodes(), G.number_of_edges()) != (1893, 13835):
        raise ValueError('Unexpected reconstructed network dimensions')
    edges=sorted((min(int(u),int(v)),max(int(u),int(v))) for u,v in G.edges())
    digest=hashlib.sha256(''.join(f'{u} {v}\n' for u,v in edges).encode()).hexdigest()
    manifest=json.loads((Path(__file__).resolve().parents[1]/'SOURCE_MANIFEST.json').read_text())
    if digest != manifest['networks']['college_message']['topology_sha256']:
        raise ValueError('Reconstructed topology does not match the paper network')
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    nx.write_gml(G, out)
    print(f'{out}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges')

if __name__ == '__main__':
    main()
