# ScholarGraph

A Python library for keeping track of claims and the evidence around them: sources, support, contradictions, confidence, and dependencies.

Imports JSON or citation CSV. Exports JSON, CSV, or Graphviz DOT.

```sh
python3.12 -m unittest discover -s tests -v
python3.12 -m scholargraph.cli sample/evidence.json
```

The example graph is synthetic. Mapping a source to a claim doesn't verify that the source is true.
