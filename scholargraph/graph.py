from __future__ import annotations
import json
from collections import deque
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass(frozen=True)
class Source: id:str; title:str; locator:str
@dataclass(frozen=True)
class Claim: id:str; text:str; confidence:float
@dataclass(frozen=True)
class Link: source:str; claim:str; relation:str; note:str

class EvidenceGraph:
 def __init__(self): self.sources={};self.claims={};self.links=[];self.dependencies={}
 def add_source(self,s:Source):
  if s.id in self.sources: raise ValueError(f"duplicate source: {s.id}")
  self.sources[s.id]=s
 def add_claim(self,c:Claim,depends_on=()):
  if c.id in self.claims or not 0<=c.confidence<=1: raise ValueError("duplicate claim or invalid confidence")
  missing=set(depends_on)-self.claims.keys()
  if missing: raise ValueError(f"unknown dependencies: {sorted(missing)}")
  self.claims[c.id]=c;self.dependencies[c.id]=set(depends_on)
 def link(self,l:Link):
  if l.source not in self.sources or l.claim not in self.claims or l.relation not in {"supports","contradicts"}: raise ValueError("invalid evidence link")
  self.links.append(l)
 def unsupported(self): return sorted(c for c in self.claims if not any(l.claim==c and l.relation=="supports" for l in self.links))
 def contradictions(self): return sorted({l.claim for l in self.links if l.relation=="contradicts"})
 def ancestors(self,claim_id):
  if claim_id not in self.claims: raise KeyError(claim_id)
  seen=set();q=deque(self.dependencies[claim_id])
  while q:
   current=q.popleft()
   if current not in seen: seen.add(current);q.extend(self.dependencies[current])
  return sorted(seen)
 def export(self): return {"sources":[asdict(x) for x in self.sources.values()],"claims":[{**asdict(x),"depends_on":sorted(self.dependencies[x.id])} for x in self.claims.values()],"links":[asdict(x) for x in self.links],"analysis":{"unsupported":self.unsupported(),"contradicted":self.contradictions()}}
 @classmethod
 def import_json(cls,path:Path):
  raw=json.loads(path.read_text());g=cls()
  for x in raw.get("sources",[]):g.add_source(Source(**x))
  for x in raw.get("claims",[]): deps=x.pop("depends_on",[]);g.add_claim(Claim(**x),deps)
  for x in raw.get("links",[]):g.link(Link(**x))
  return g
