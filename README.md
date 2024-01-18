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
