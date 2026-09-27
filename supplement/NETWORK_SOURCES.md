# Empirical network sources

## College Message

The source dataset is the Stanford SNAP **CollegeMsg temporal network**, derived from Panzarasa, Opsahl & Carley (2009). The published SNAP file has directed temporal message records. For Experiment 3 we drop timestamps, replace the directed relation with an undirected relation (an edge exists if either user messaged the other), and retain the largest connected component. The resulting graph has 1,893 nodes and 13,835 edges.

`scripts/prepare_college_message.py` reconstructs the supplied `college_message.gml` from the public SNAP download and verifies those counts.

Source page: `https://snap.stanford.edu/data/CollegeMsg.html`

Suggested citations:

- Panzarasa, P., Opsahl, T. & Carley, K. M. (2009), *Patterns and dynamics of users' behavior and interaction: Network analysis of an online community*.
- Leskovec, J. & Krevl, A. (2014), *SNAP Datasets: Stanford Large Network Dataset Collection*.

## Francis Bacon

The second topology is a snapshot of the **Six Degrees of Francis Bacon** network, file `francisbacon-2023-04-23.gml`. The snapshot used in the project has 13,032 nodes and 171,540 undirected edges.

Project/method reference: Warren et al. (2016), *Six Degrees of Francis Bacon: A Statistical Method for Reconstructing Large Historical Social Networks*.

The exact snapshot's SHA-256 is recorded in `SOURCE_MANIFEST.json`.

### Redistribution note

Redistribution terms for this exact GML snapshot have not been established, so it is excluded from the public checkout and remains covered by `.gitignore`. The six Francis Bacon Experiment 3 conditions require this exact snapshot to be obtained separately and placed at `supplement/networks/francisbacon-2023-04-23.gml` (relative to the repository root). The configurations, checksum and source documentation remain included; a different snapshot is not a substitute for these conditions.

Run `python supplement/scripts/validate_supplement.py` for the public checkout; it reports the absent snapshot explicitly. When both this exact snapshot and the supplied College Message file are available locally, use `python supplement/scripts/validate_supplement.py --require-all-networks` to require both files and verify their checksums and topologies. Keep the Francis Bacon file local unless its redistribution terms have been established.
