import tempfile,unittest
from pathlib import Path
from scholargraph.graph import *
from scholargraph.analysis import *
from scholargraph.exporters import *
from scholargraph.citation_import import import_sources_csv
class AnalysisTests(unittest.TestCase):
 def graph(self):
  g=EvidenceGraph();g.add_source(Source("s","Demo","demo:s"));g.add_claim(Claim("a","Base",.8));g.add_claim(Claim("b","Child",.5),["a"]);g.link(Link("s","a","supports","x"));return g
 def test_depth_balance_and_fragility(self):
  g=self.graph();self.assertEqual(dependency_depths(g),{"a":0,"b":1});self.assertEqual(evidence_balance(g)["a"]["net"],1);self.assertEqual(fragile_claims(g),["b"])
 def test_exports(self):
  g=self.graph();self.assertIn('"a" -> "b"',to_dot(g));self.assertIn("source,claim,relation,note",links_csv(g))
 def test_csv_import(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"sources.csv";p.write_text("id,title,locator\ns1,Synthetic,demo:1\n");g=import_sources_csv(EvidenceGraph(),p);self.assertIn("s1",g.sources)
