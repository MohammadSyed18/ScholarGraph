import csv
from pathlib import Path
from .graph import Source
def import_sources_csv(graph,path:Path):
 with path.open(newline="") as handle:
  for row in csv.DictReader(handle):
   if not {"id","title","locator"}<=row.keys():raise ValueError("citation CSV requires id,title,locator")
   graph.add_source(Source(row["id"],row["title"],row["locator"]))
 return graph
