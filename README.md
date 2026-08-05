# ScholarGraph

A Python evidence-mapping library for claims, sources, support, contradictions, confidence, and provenance. It imports a neutral JSON format, traverses claim dependencies, identifies unsupported or contradicted claims, and exports an analysis snapshot.

Run `python3.12 -m unittest discover -s tests -v` and `python3.12 -m scholargraph.cli sample/evidence.json`. The example is explicitly synthetic; ScholarGraph does not verify source truth or provide research conclusions.
