"""Evidence coverage queries and source-removal sensitivity analysis."""

from collections import defaultdict, deque
from .analysis import dependency_depths, impact_report


def source_sensitivity(graph, removed_sources):
    removed = set(removed_sources)
    if removed - graph.sources.keys():
        raise ValueError("unknown source in removal set")
    result = []
    for claim in graph.claims.values():
        before = {
            link.source
            for link in graph.links
            if link.claim == claim.id and link.relation == "supports"
        }
        after = before - removed
        if before != after:
            result.append(
                {
                    "claim": claim.id,
                    "sources_before": len(before),
                    "sources_after": len(after),
                    "loses_all_support": bool(before) and not after,
                    "removed_support": sorted(before & removed),
                }
            )
    changed = [item["claim"] for item in result if item["loses_all_support"]]
    return {
        "direct_changes": result,
        "downstream_review": impact_report(graph, changed),
    }


def review_queue(graph, *, minimum_sources=2):
    if type(minimum_sources) is not int or minimum_sources < 1:
        raise ValueError("minimum_sources must be positive")
    depths = dependency_depths(graph)
    result = []
    for claim in graph.claims.values():
        supporting = {
            link.source
            for link in graph.links
            if link.claim == claim.id and link.relation == "supports"
        }
        opposing = {
            link.source
            for link in graph.links
            if link.claim == claim.id and link.relation == "contradicts"
        }
        reasons = []
        if not supporting:
            reasons.append("no supporting source")
        elif len(supporting) < minimum_sources:
            reasons.append("limited source coverage")
        if opposing:
            reasons.append("contradicting evidence")
        if supporting & opposing:
            reasons.append("same source linked with both polarities")
        if claim.confidence >= 0.8 and len(supporting) < minimum_sources:
            reasons.append("high confidence with limited coverage")
        if reasons:
            result.append(
                {
                    "id": claim.id,
                    "text": claim.text,
                    "confidence": claim.confidence,
                    "supporting_sources": sorted(supporting),
                    "opposing_sources": sorted(opposing),
                    "depth": depths[claim.id],
                    "reasons": reasons,
                    "priority": 4 * int(not supporting)
                    + 2 * len(opposing)
                    + int(claim.confidence >= 0.8),
                }
            )
    return sorted(
        result, key=lambda item: (-item["priority"], item["depth"], item["id"])
    )


def evidence_paths(graph, claim_id):
    """Return root-to-claim dependency paths and their directly attached sources."""
    if claim_id not in graph.claims:
        raise KeyError(claim_id)
    paths = []
    stack = [(claim_id, [claim_id])]
    while stack:
        current, path = stack.pop()
        parents = sorted(graph.dependencies[current], reverse=True)
        if not parents:
            nodes = list(reversed(path))
            sources = sorted(
                {link.source for link in graph.links if link.claim in nodes}
            )
            paths.append({"claims": nodes, "sources": sources})
        for parent in parents:
            if parent in path:
                raise ValueError("dependency cycle")
            stack.append((parent, path + [parent]))
        if len(paths) + len(stack) > 10000:
            raise ValueError("too many dependency paths; query a smaller subgraph")
    return paths


def markdown_review(graph):
    def safe(value):
        return (
            str(value)
            .replace("\\", "\\\\")
            .replace("|", "\\|")
            .replace("\n", " ")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    lines = [
        "# Evidence review",
        "",
        "| Claim | Sources for | Sources against | Review reasons |",
        "| --- | ---: | ---: | --- |",
    ]
    for item in review_queue(graph):
        lines.append(
            f"| {safe(item['id'])}: {safe(item['text'])} | {len(item['supporting_sources'])} | {len(item['opposing_sources'])} | {safe('; '.join(item['reasons']))} |"
        )
    if not review_queue(graph):
        lines += ["", "No claims triggered the configured coverage checks."]
    lines += [
        "",
        "Coverage and contradiction flags organize review; they do not verify source truth.",
    ]
    return "\n".join(lines) + "\n"
