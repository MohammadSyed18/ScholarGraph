import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from scholargraph.graph import EvidenceGraph, Source, Claim, Link
from scholargraph.review import (
    source_sensitivity,
    review_queue,
    evidence_paths,
    markdown_review,
)
from scholargraph.storage import GraphStore, RevisionConflict


def populate(graph):
    graph.add_source(Source("s", "Study", "https://example.org"))
    graph.add_claim(Claim("root", "Main | claim", 0.9))
    graph.add_claim(Claim("leaf", "Dependent", 0.7), ["root"])
    graph.link(Link("s", "root", "supports", "measurement"))


class ReviewStorageTests(unittest.TestCase):
    def test_removal_propagates_review_without_mutating_graph(self):
        graph = EvidenceGraph()
        populate(graph)
        report = source_sensitivity(graph, ["s"])
        self.assertEqual(
            [item["claim"] for item in report["downstream_review"]], ["root", "leaf"]
        )
        self.assertEqual(evidence_paths(graph, "leaf")[0]["claims"], ["root", "leaf"])
        self.assertEqual(len(graph.links), 1)
        self.assertIn("Main \\| claim", markdown_review(graph))
        self.assertEqual(review_queue(graph)[0]["id"], "leaf")

    def test_atomic_edit_and_revision_conflict(self):
        with TemporaryDirectory() as directory:
            store = GraphStore(Path(directory) / "graph.json")
            revision, graph = store.update(0, populate)
            self.assertEqual(revision, 1)
            with self.assertRaises(RevisionConflict):
                store.update(0, lambda graph: None)
            before = store.path.read_text()

            def corrupt(graph):
                graph.dependencies["root"].add("missing")

            with self.assertRaises(ValueError):
                store.update(1, corrupt)
            self.assertEqual(store.path.read_text(), before)
            self.assertEqual(store.load()[1].export(), graph.export())
