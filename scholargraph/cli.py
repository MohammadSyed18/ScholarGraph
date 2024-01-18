import argparse
import json
from pathlib import Path
from .graph import EvidenceGraph
from .review import markdown_review


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--review", action="store_true")
    args = parser.parse_args()
    graph = EvidenceGraph.import_json(args.input)
    text = (
        markdown_review(graph) if args.review else json.dumps(graph.export(), indent=2)
    )
    if args.out:
        args.out.write_text(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
