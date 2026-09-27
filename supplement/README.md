# Structure Meets Strategy reproducibility supplement

This package reconstructs the experimental designs in *Structure Meets Strategy in the Misinformation Age*. It supplies configurations, runnable analysis code, the College Message network, and source information. The Francis Bacon dataset must be obtained separately as described in `NETWORK_SOURCES.md`. Historical raw simulation results are not distributed. Fresh runs will not reproduce the original random draws, sample counts or numerical results exactly.

Start with the setup instructions below. `ANALYSIS_NOTES.md` explains outcome definitions, statistical specifications and the scope of each analysis workflow.

## Layout

- `configs/`: compact specifications; generated runnable YAML goes in ignored `configs/generated/`.
- `analysis/experiment_1/`: clean notebook entry points for corrected fresh summaries and comparisons.
- `analysis/experiment_2/`: runnable multivariate and robustness notebook.
- `networks/`: the supplied College Message GML file. The Francis Bacon snapshot is excluded from the public checkout because its redistribution terms have not been established.
- `scripts/`: validation, generation, preprocessing, summary and model-fitting tools.

## Reference environment

Tested on Linux x86_64 with Python 3.11.16, CPU Torch 2.2.0, DGL 2.1.0 and TorchData 0.7.1. Windows and macOS execution have not been tested. Windows users can use a Linux environment such as WSL for the tested analysis stack.

The pinned PolyGraphs commit is `f2c8d416c3affafb7215e40f0dd0b79549649ebc`. This is a replication reference, not proof of every historical checkout. The simulator source is unchanged between the recorded preceding simulation-code commit and this reference commit. Dependencies are a tested reference environment, not a reconstruction of every historical workstation.

The `francisbacon` commit `1e0f25db2c2a1e8abf5367e10525794918bb53e8` from `Prudhvivuda/polygraphs` is preserved in [Software Heritage](https://archive.softwareheritage.org/swh:1:rev:1e0f25db2c2a1e8abf5367e10525794918bb53e8/). The archive visit completed with status `full`, and the exact revision was independently retrieved. A complete Git-tree comparison showed that all 118 files in this version match the pinned upstream version exactly; upstream adds only `codemeta.json`. This establishes source-code equivalence, not which checkout was used for every historical simulation. `SOURCE_MANIFEST.json` records the archive identifiers. This source archive does not resolve the missing historical simulation outputs or the separately required Francis Bacon dataset.

From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r supplement/requirements-analysis.txt
python supplement/scripts/validate_supplement.py
```

Public validation reports the absent Francis Bacon snapshot explicitly; its six Experiment 3 conditions cannot run without that file. Use `python supplement/scripts/validate_supplement.py --require-all-networks` only when both network files are available locally.

TorchData is pinned because DGL 2.1.0 imports its older DataPipes API. Import errors fail validation. `--static-only` is available for file inspection, but explicitly does not certify the installed environment. No validation mode constitutes full numerical replication.

## Generate and run configurations

```bash
python supplement/scripts/generate_configs.py
python -m polygraphs.run --configure supplement/configs/generated/e1_BalaGoyalOp_r1.0_m1.yaml
```

There are 341 configurations: 78 main Experiment 1 cells, 5 additional Zollman cells, 246 Experiment 2 cells including benchmarks, and 12 empirical-network cells. Their configured repeat counts total 33,060 fresh simulations. This is a substantial computation; a successful short test is not a reason to run the whole grid unintentionally.

Run each YAML as a **separate invocation**. Passing multiple configurations to `--configure` merges them; it does not run a batch. `scripts/run_configs.py` provides an explicit batch runner:

```bash
python supplement/scripts/run_configs.py 'e1_*.yaml'
```

Outputs go to `supplement/outputs/experiment_1/`, `experiment_2/`, `experiment_3/college_message/` and `experiment_3/francis_bacon/`. Run commands from the repository root. Do not mix smoke-test outputs with scientific runs.

The seed is 123456789, supported by recovered Experiment 1 configurations but not established for every historical batch. Separate config invocations restart that seed. Repeats within each invocation advance the random state. Re-running a config with the same seed produces duplicate stochastic sequences; do not pool such reruns as independent observations. Different conditions can share random draws because they start from the same seed; the historical reconstruction does not establish an independent per-cell seed schedule.

## Experiment 1

The main grid uses 64-agent Barabási-Albert graphs with attachments 1, 2, 4, 8, 16 and 32; a pristine condition and four unreliable operations at r = 0.75, 0.5 and 0.25; 100 repeats per cell; and a 100,000-step horizon. The 32-agent Zollman subset uses gullible misinformation at r = 0.25 and attachments 1, 2, 4, 8, 16, with 50, 25, 25, 100, 100 repeats.

```bash
python supplement/scripts/build_experiment1_dataframe.py supplement/outputs/experiment_1
python supplement/scripts/analyse_experiment1.py supplement/analysis/experiment_1/raw_data/bigsimpleframe.csv
```

Results are `analysis/experiment_1/results/summary.csv` and `comparisons.csv`. Accuracy is B/(A+B), undefined when no run converges; efficiency uses B runs only. Count-based chi-squared, Fisher exact and Mann-Whitney comparisons are fresh analyses, not reproductions of historical p-values. P-values are unadjusted and comparison scopes are documented in `ANALYSIS_NOTES.md`. The two notebooks in this directory are optional views of these outputs; launch Jupyter from that directory.

## Experiment 2

64-agent networks, epsilon 0.001 and a 100,000-step horizon. Main factorial conditions use nominal reliability 0.75 and gullible/aligned misinformation/disinformation. Pristine and Ideal are separate benchmarks.

- BA attachments: 1, 2, 4, 8, 16, 32.
- ER probabilities: 0.12, 0.22, 0.24, 0.36, 0.38, 0.48, 0.50.
- WS neighbours: 2, 4, 8, 14, 16, 24, 32; rewiring: 0, 0.25, 0.50, 0.75.

```bash
python supplement/scripts/build_experiment2_seed_csv.py supplement/outputs/experiment_2
python supplement/scripts/fit_experiment2.py supplement/analysis/experiment_2/raw_data/main_factorial.csv
```

The preprocessor computes density, average local clustering, average shortest path length and reliable-node count from each saved graph. Structural metrics exclude self-loops. The fitting script uses the documented fixed final specifications, including the accepted environment-by-reliable-count term for efficiency. Continuous predictors use means and sample SDs from the full accuracy sample for both outcomes. Reference categories are disinformation, aligned and Barabási-Albert.

The optional `analysis/experiment_2/multivariate_analysis.ipynb` retains the historical model-selection sequence and robustness analyses, with portability fixes and the missing final efficiency assignment restored. Launch Jupyter from that notebook's directory. Its historical narrative and fixed main-model decisions must not be read as new selection results. Inspect fit diagnostics, separation, warnings and standard errors before interpreting any rerun. This workflow provides the specified regressions and robustness analyses; it does not supply a historical FDR-adjusted univariate analysis.

## Experiment 3

College Message has 1,893 nodes and 13,835 undirected edges, with 50 repeats per condition. Francis Bacon has 13,032 nodes and 171,540 edges, with 10 repeats per condition. Both use six conditions and a 25,000-step horizon.

College Message is supplied. To run the six Francis Bacon conditions, obtain the exact snapshot described in `NETWORK_SOURCES.md` separately and place it at `supplement/networks/francisbacon-2023-04-23.gml`. Its configurations, checksum and provenance are retained in the public checkout.

```bash
python supplement/scripts/summarise_experiment3.py supplement/outputs/experiment_3/college_message --output supplement/analysis/experiment_3/results/college_message_summary.csv
python supplement/scripts/summarise_experiment3.py supplement/outputs/experiment_3/francis_bacon --output supplement/analysis/experiment_3/results/francis_bacon_summary.csv
```

At each recorded time and condition the script computes the pooled agent mean, pooled 25th percentile, and mean of within-simulation sample SDs (ddof=1). It processes one condition/time at a time to avoid retaining hundreds of millions of rows. It reports contributing simulation and agent counts. Runs with no snapshot at a time do not contribute; terminated trajectories are not carried forward.

**Implementation distinction:** the pinned GML loader does not add self-loops, even when `network.selfloop` is true. Synthetic generators do. The revised package preserves the pinned simulator and supplied topologies. This distinction affects own-evidence handling across experiments, as described in `ANALYSIS_NOTES.md`.

College Message can be reconstructed with `python supplement/scripts/prepare_college_message.py`. A reconstructed serialization may differ byte-for-byte while preserving topology; the original distributed file's checksum is used by the release validator. The reconstruction script checks topology, not only dimensions.

## What is excluded

Historical raw outputs, new simulation outputs, generated configs, notebook outputs, machine-specific paths, incidental personal headers, old repository notebook locations, and paper-only figure-production cells are excluded from the public workflow. Archived source notebooks and historical count tables are also excluded; they are not inputs to the current workflow. Authorship and copyright remain in root CITATION.cff/LICENSE; source repository identifiers remain in provenance URLs. This is not an anonymous-review package.
