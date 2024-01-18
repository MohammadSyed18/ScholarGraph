# scholargraph

a Python library for keeping track of claims and the evidence around them: sources, support, contradictions, confidence, and dependencies.

imports JSON or citation CSV. Exports JSON, CSV, or Graphviz DOT.

```sh
python3.12 -m unittest discover -s tests -v
python3.12 -m scholargraph.cli sample/evidence.json
```

the example graph is synthetic. mapping a source to a claim doesn't verify that the source is true.

## Implementation details

JSON imports resolve claims in dependency order, independent of file order. `impact_report(graph, changed_claims)` identifies downstream claims requiring review and reports their evidence-source counts.

## Evidence review and storage

[review.py](scholargraph/review.py) builds prioritized review queues, root-to-claim evidence paths, and source-removal sensitivity reports. Sources are counted by identity rather than link count. Removing the final supporting source flags downstream claims for review without mutating the graph.

[storage.py](scholargraph/storage.py) adds revision-checked snapshots. Edits stage on a copy, references are revalidated, and a POSIX file lock protects read/modify/write operations. Writes flush before atomic replacement; stale expected revisions raise `RevisionConflict`. Snapshot locking currently targets macOS/Linux.

```sh
python -m scholargraph.cli sample/evidence.json --review
python -m unittest discover -s tests -v
```

Use `GraphStore(path).update(expected_revision, operation)` to persist an edit, and `load()` to retrieve its revision and graph. Tests cover failed-edit rollback, revision conflicts, source-removal propagation, read-only queries, and escaped Markdown tables.
