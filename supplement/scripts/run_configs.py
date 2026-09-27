#!/usr/bin/env python3
"""Run matching generated configurations separately. Each uses its full configured repeat count."""
import argparse,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('pattern',help='Quoted filename glob, e.g. e1_*.yaml');a=p.parse_args()
root=Path(__file__).resolve().parents[2]
paths=sorted((root/'supplement/configs/generated').glob(a.pattern))
if not paths:raise SystemExit('No matching configurations. Generate them first.')
for path in paths:subprocess.run([sys.executable,'-m','polygraphs.run','--configure',str(path)],cwd=root,check=True)
