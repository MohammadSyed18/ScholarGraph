import csv,io
def to_dot(graph):
 lines=["digraph evidence {"]
 for claim in graph.claims.values():lines.append(f'  "{claim.id}" [label="{claim.text.replace(chr(34),chr(39))}"];')
 for child,parents in graph.dependencies.items():
  for parent in parents:lines.append(f'  "{parent}" -> "{child}" [label="depends"];')
 for link in graph.links:lines.append(f'  "{link.source}" -> "{link.claim}" [label="{link.relation}"];')
 return "\n".join(lines+["}"])
def links_csv(graph):
 out=io.StringIO();w=csv.writer(out);w.writerow(["source","claim","relation","note"]);w.writerows((x.source,x.claim,x.relation,x.note) for x in graph.links);return out.getvalue()
