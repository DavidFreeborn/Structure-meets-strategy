# Analysis methods and provenance

## Experiment 1

Use the scripts under `scripts/` and notebooks under `analysis/` for fresh analyses. The supported Experiment 1 workflow uses observed counts in chi-squared tests and restricts comparisons to the reconstructed design; it does not reproduce the historical notebooks' percentage-based tests.

The clean workflow counts A, B and non-convergence separately. Conditional accuracy is B/(A+B); no convergence yields a missing value, not zero accuracy. Efficiency means and medians use only B runs. For each network size, pairwise comparisons vary exactly one of operation, reliability or attachment count, holding the other dimensions fixed. In addition, the pristine baseline is compared with each unreliable operation/reliability at the same size and attachment count. The 32-agent analysis is restricted to the manuscript's gullible-misinformation r=0.25 subset.

Chi-squared tests use the observed two-by-two outcome counts with the historical SciPy default continuity correction. Fisher exact p-values and minimum expected counts are also reported. No outcome variation or missing converged groups is explicitly identified instead of replacing an invalid test with p=1. Mann-Whitney tests compare successful-run step counts, two-sided. These outputs are unadjusted fresh comparisons, not confirmation of historical significance; interpret multiplicity accordingly. The script does not purport to recover the original family of hypothesis tests.

## Experiment 2

The four main operations are coded as disinfo/misinfo and aligned/gullible. Pristine and Ideal simulations are benchmarks and are excluded from the factorial regressions. Accuracy is action B within 100,000 steps; efficiency is steps among those successes. Network metrics use the loop-free undirected graph produced by the pinned Processor converter. Disconnected graphs are rejected in the main preprocessor, matching the manuscript's connected-network design.

The fixed-specification runner fits the declared final accuracy blocks C+E+G and efficiency blocks A+E+H-prime, retaining all first-order terms. It uses the full accuracy sample for centring and sample-SD scaling of all continuous predictors, including when fitting efficiency. It saves coefficients, standard errors, confidence intervals, p-values, model summaries, formulas, scaling values and fit diagnostics. It rejects non-converged or nonfinite fits after writing diagnostics. Convergence alone does not establish absence of separation or model adequacy.

The portable historical notebook retains the original sequence of candidate fits and robustness replays. Its hard-coded main assignments represent historical retained blocks; printed selection decisions can differ on fresh data. Final efficiency results include the accepted H-prime interaction. The optional plotting section was removed; numerical analyses and robustness sections are retained. Historical narrative conclusions are preserved as historical commentary, not certified results for a new sample. Regressions require sufficient successful and unsuccessful runs and variation in every predictor. The full notebook has not been executed against a newly generated full-size archive; the documented testing establishes software operation rather than numerical replication of historical results.

## Experiment 3

The supported summary uses pooled agent-level mean and 25th percentile, plus sample SD within each simulation averaged across simulations (ddof=1). These match the intended quantities in the manuscript and the relevant historical notebook sections. The old exploratory comparisons, centrality analyses and time-point hypothesis tests are not used.

Only available recorded iterations contribute. No extrapolation or forward filling is introduced. Each output row includes the number of contributing simulations and agents. Reading one condition/time at a time greatly reduces memory compared with concatenating all agent-time rows.

## Implementation and provenance

The pinned synthetic graph generators add self-loops, while the GML loader does not. The package preserves this implementation distinction. In default/gullible processing, own evidence enters the incoming evidence pool through self-loops. Modified aligned processing applies Jeffrey updating to incoming evidence and then Bayesian updating to the node's own payoff. Consequently, its own payoff enters both stages in synthetic graphs but only the latter stage in the empirical graphs. Unreliable nodes use the unreliable sampler for their own payoff; there is no separate retained truthful private observation.

`SOURCE_MANIFEST.json` records the pinned simulator version, original analysis source identities and checksums for both reference networks. Archived source notebooks and historical count tables are not distributed or required by validation. The runnable Experiment 2 notebook is retained because it provides model-selection and robustness analyses beyond the fixed-specification regression script.

Local notebook names and analysis paths use experiment/function names. Incidental references to individual collaborators have been removed. Copyright and author records are retained in the root LICENSE and CITATION.cff. Necessary source repository names and remote paths remain in the provenance manifest; changing them would break source identification. Names of cited researchers, established models and the historical empirical network are not incidental collaborator labels. Historical-person attributes inside the empirical GML are preserved with the exact dataset.
