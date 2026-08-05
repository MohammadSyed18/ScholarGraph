import json,tempfile,unittest
from pathlib import Path
from scholargraph.graph import *
class GraphTests(unittest.TestCase):
 def test_traversal_and_analysis(self):
  g=EvidenceGraph();g.add_source(Source("s","Synthetic observation","demo:s"));g.add_claim(Claim("a","Measured value",.8));g.add_claim(Claim("b","Derived interpretation",.5),["a"]);g.link(Link("s","a","supports","sample"));g.link(Link("s","b","contradicts","sample disagreement"));self.assertEqual(g.ancestors("b"),["a"]);self.assertEqual(g.unsupported(),["b"]);self.assertEqual(g.contradictions(),["b"])
 def test_import_rejects_unknown_provenance(self):
  raw={"sources":[],"claims":[{"id":"c","text":"x","confidence":.5}],"links":[{"source":"missing","claim":"c","relation":"supports","note":"x"}]}
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"x.json";p.write_text(json.dumps(raw));self.assertRaises(ValueError,EvidenceGraph.import_json,p)
