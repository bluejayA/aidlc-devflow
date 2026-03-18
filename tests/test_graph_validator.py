"""L1 Graph Validator — static structural validation of JSON graphs.

Validates:
1. No dead-ends (all gate-option targets are valid)
2. No unreachable steps (all steps reachable from entry)
3. No unknown external refs (referenced skills exist)
4. No infinite circular loops (escape conditions exist)
5. Option completeness (each gate has >= 2 options)
"""

from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).parent.parent / "skills"

ORCHESTRATORS = [
    "aidlc-inception-orchestrator",
    "aidlc-construction-orchestrator",
]

# Logical actions: gate-option targets that represent workflow actions
# rather than graph nodes (e.g., 'next-unit', 'INCEPTION-complete').
LOGICAL_ACTIONS = {
    "next-unit",
    "branch-name-confirm",
    "inception-routing",
    "code-generation-plan",
    "code-generation-generate",
}


# --- Helpers ---


def collect_node_ids(graph: dict) -> set[str]:
    """Collect all valid node IDs (step ids + gate ids) in a graph."""
    ids = set()
    for step in graph.get("steps", []):
        ids.add(step["id"])
    for gate in graph.get("gates", []):
        ids.add(gate["id"])
    return ids


def collect_targets(graph: dict) -> set[str]:
    """Collect all targets referenced by gate-options and conditions."""
    targets = set()
    for gate in graph.get("gates", []):
        for opt in gate.get("options", []):
            targets.add(opt["target"])
    for cond in graph.get("conditions", []):
        targets.add(cond["target"])
    return targets


def is_external_ref(target: str) -> bool:
    """Check if a target is an external ref, phase transition, or logical action."""
    if "/" in target:
        return True
    if target.startswith("CONSTRUCTION") or target.startswith("INCEPTION"):
        return True
    return target in LOGICAL_ACTIONS


def skill_exists(name: str) -> bool:
    """Check if a skill directory exists."""
    return (SKILLS_DIR / name).is_dir() or (SKILLS_DIR / f"aidlc-{name}").is_dir()


def build_adjacency(graph: dict) -> dict[str, set[str]]:
    """Build adjacency list from graph: node -> set of reachable nodes."""
    adj: dict[str, set[str]] = {}
    node_ids = collect_node_ids(graph)

    for gate in graph.get("gates", []):
        neighbors = set()
        for opt in gate.get("options", []):
            if opt["target"] in node_ids:
                neighbors.add(opt["target"])
        adj[gate["id"]] = neighbors

    for cond in graph.get("conditions", []):
        if cond["target"] in node_ids:
            adj.setdefault("__conditions__", set()).add(cond["target"])

    return adj


def reachable_from(start: str, adj: dict[str, set[str]], all_ids: set[str]) -> set[str]:
    """BFS/DFS to find all reachable node IDs from start."""
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        for neighbor in adj.get(node, set()):
            if neighbor not in visited:
                stack.append(neighbor)
    return visited


def build_full_adjacency(graph: dict) -> dict[str, set[str]]:
    """Build complete adjacency including step sequence, gate sequence, and transitions."""
    node_ids = collect_node_ids(graph)
    adj = build_adjacency(graph)

    steps = sorted(graph["steps"], key=lambda s: s["order"])
    for i in range(len(steps) - 1):
        adj.setdefault(steps[i]["id"], set()).add(steps[i + 1]["id"])

    gates = graph.get("gates", [])
    for i in range(len(gates) - 1):
        adj.setdefault(gates[i]["id"], set()).add(gates[i + 1]["id"])

    if steps and gates:
        adj.setdefault(steps[-1]["id"], set()).add(gates[0]["id"])

    for gate in gates:
        for opt in gate["options"]:
            t = opt["target"]
            if t in node_ids:
                adj.setdefault(gate["id"], set()).add(t)

    return adj


def find_unreachable(graph: dict) -> set[str]:
    """Find unreachable nodes from the first step."""
    if not graph["steps"]:
        return set()

    node_ids = collect_node_ids(graph)
    adj = build_full_adjacency(graph)

    steps = sorted(graph["steps"], key=lambda s: s["order"])
    start = steps[0]["id"]
    reached = reachable_from(start, adj, node_ids)

    for cond_target in adj.get("__conditions__", set()):
        reached |= reachable_from(cond_target, adj, node_ids)

    return node_ids - reached


# --- Tests (parametrized over orchestrators) ---


@pytest.mark.parametrize("name", ORCHESTRATORS)
class TestNoDeadEnds:
    """Every gate-option target must be a valid node or external ref."""

    def test_no_dead_ends(self, load_graph, name):
        graph = load_graph(name)
        node_ids = collect_node_ids(graph)
        dead_ends = [
            t for t in collect_targets(graph)
            if t not in node_ids and not is_external_ref(t) and not skill_exists(t)
        ]
        assert dead_ends == [], f"Dead-end targets in {name}: {dead_ends}"


@pytest.mark.parametrize("name", ORCHESTRATORS)
class TestOptionCompleteness:
    """Each gate must have at least 2 options."""

    def test_option_completeness(self, load_graph, name):
        graph = load_graph(name)
        incomplete = [g["id"] for g in graph["gates"] if len(g["options"]) < 2]
        assert incomplete == [], f"Gates with < 2 options in {name}: {incomplete}"


@pytest.mark.parametrize("name", ORCHESTRATORS)
class TestNoUnreachable:
    """All steps and gates should be reachable from the first step."""

    def test_no_unreachable(self, load_graph, name):
        graph = load_graph(name)
        unreachable = find_unreachable(graph)
        assert unreachable == set(), f"Unreachable nodes in {name}: {unreachable}"


@pytest.mark.parametrize("name", ORCHESTRATORS)
class TestNoUnknownRefs:
    """External skill references must point to existing skill directories."""

    def test_no_unknown_refs(self, load_graph, name):
        graph = load_graph(name)
        node_ids = collect_node_ids(graph)
        unknown = [
            t for t in collect_targets(graph)
            if t not in node_ids and not is_external_ref(t) and not skill_exists(t)
        ]
        assert unknown == [], f"Unknown external refs in {name}: {unknown}"


@pytest.mark.parametrize("name", ORCHESTRATORS)
class TestNoCircular:
    """Gate self-references must have an escape option."""

    def test_no_infinite_loops(self, load_graph, name):
        graph = load_graph(name)
        for gate in graph["gates"]:
            self_refs = [o for o in gate["options"] if o["target"] == gate["id"]]
            if self_refs:
                escape_refs = [o for o in gate["options"] if o["target"] != gate["id"]]
                assert len(escape_refs) >= 1, (
                    f"Gate '{gate['id']}' in {name} has self-reference but no escape"
                )
