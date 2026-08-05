# ScholarGraph

A Python evidence-mapping library for claims, sources, support, contradictions, confidence, and provenance. It imports neutral JSON or citation CSV, traverses dependencies, calculates evidence balance and claim depth, identifies fragile claims, and exports JSON, CSV, or Graphviz DOT.

Run `python3.12 -m unittest discover -s tests -v` and `python3.12 -m scholargraph.cli sample/evidence.json`. The example is explicitly synthetic; ScholarGraph does not verify source truth or provide research conclusions.
