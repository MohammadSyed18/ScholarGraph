import json, tempfile, unittest
from pathlib import Path
from scholargraph.graph import EvidenceGraph
from scholargraph.analysis import impact_report


class ImportIntegrity(unittest.TestCase):
    def load(self, claims):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "graph.json"
            path.write_text(json.dumps({"claims": claims}))
            return EvidenceGraph.import_json(path)

    def test_dependency_order_is_independent_of_file_order(self):
        graph = self.load(
            [
                {"id": "b", "text": "child", "confidence": 0.6, "depends_on": ["a"]},
                {"id": "a", "text": "root", "confidence": 0.7},
            ]
        )
        self.assertEqual([x["claim"] for x in impact_report(graph, ["a"])], ["a", "b"])

    def test_cycles_and_duplicates_rejected(self):
        for claims in [
            [
                {"id": "a", "text": "x", "confidence": 0.5, "depends_on": ["b"]},
                {"id": "b", "text": "y", "confidence": 0.5, "depends_on": ["a"]},
            ],
            [{"id": "a", "text": "x", "confidence": 0.5}] * 2,
        ]:
            with self.assertRaises(ValueError):
                self.load(claims)
