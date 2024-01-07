import argparse,json
from pathlib import Path
from .graph import EvidenceGraph
def main():
 p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--out",type=Path);a=p.parse_args();data=EvidenceGraph.import_json(a.input).export();text=json.dumps(data,indent=2);a.out.write_text(text+"\n") if a.out else print(text)
if __name__=="__main__":main()
