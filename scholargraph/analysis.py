from collections import defaultdict


def evidence_balance(graph):
    counts = defaultdict(lambda: {"supports": 0, "contradicts": 0})
    for link in graph.links:
        counts[link.claim][link.relation] += 1
    return {
        claim: {
            **counts[claim],
            "net": counts[claim]["supports"] - counts[claim]["contradicts"],
        }
        for claim in graph.claims
    }


def dependency_depths(graph):
    memo = {}

    def depth(node, visiting=frozenset()):
        if node in visiting:
            raise ValueError("dependency cycle")
        if node not in memo:
            memo[node] = (
                0
                if not graph.dependencies[node]
                else 1
                + max(depth(x, visiting | {node}) for x in graph.dependencies[node])
            )
        return memo[node]

    return {node: depth(node) for node in graph.claims}


def fragile_claims(graph):
    return sorted(
        c
        for c, v in evidence_balance(graph).items()
        if v["supports"] <= v["contradicts"]
    )


def impact_report(graph, changed_claims):
    """Find downstream claims whose conclusions need review after a change."""
    from collections import deque

    changed = set(changed_claims)
    if changed - graph.claims.keys():
        raise ValueError("unknown changed claim")
    children = defaultdict(set)
    for child, parents in graph.dependencies.items():
        for parent in parents:
            children[parent].add(child)
    queue = deque(sorted(changed))
    affected = set(changed)
    while queue:
        for child in sorted(children[queue.popleft()]):
            if child not in affected:
                affected.add(child)
                queue.append(child)
    depths = dependency_depths(graph)
    return [
        {
            "claim": claim,
            "direct_change": claim in changed,
            "depth": depths[claim],
            "source_count": len({x.source for x in graph.links if x.claim == claim}),
        }
        for claim in sorted(affected, key=lambda key: (depths[key], key))
    ]
