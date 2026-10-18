"""L2 Routing Simulator — YAML fixture-based orchestrator simulation.

Uses the routing engine to simulate orchestrator routing on JSON graphs
with deterministic inputs and compares results to expected paths.
"""

import json
from pathlib import Path

import pytest
import yaml

from routing_engine import simulate

TESTS_DIR = Path(__file__).parent
GRAPH_DIR = TESTS_DIR / "graph"
SCENARIOS_DIR = TESTS_DIR / "scenarios"


# --- Tests ---


def _load_scenarios():
    """Load all YAML scenario files."""
    scenarios = []
    if not SCENARIOS_DIR.exists():
        return scenarios
    for path in sorted(SCENARIOS_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        data["_file"] = path.name
        scenarios.append(data)
    return scenarios


def _scenario_ids():
    return [s["_file"].replace(".yaml", "") for s in _load_scenarios()]


@pytest.mark.parametrize("scenario", _load_scenarios(), ids=_scenario_ids())
def test_scenario(scenario):
    """Run scenario and compare stage_path."""
    graph_path = GRAPH_DIR / f"{scenario['orchestrator']}.json"
    assert graph_path.exists(), f"Graph not found: {graph_path}"

    graph = json.loads(graph_path.read_text())
    result = simulate(graph, scenario["inputs"])

    expected_path = scenario["expect"]["stage_path"]
    expected_final = scenario["expect"]["final_stage"]

    assert result["stage_path"] == expected_path, (
        f"Stage path mismatch in '{scenario['name']}':\n"
        f"  expected: {expected_path}\n"
        f"  actual:   {result['stage_path']}"
    )
    assert result["final_stage"] == expected_final, (
        f"Final stage mismatch in '{scenario['name']}':\n"
        f"  expected: {expected_final}\n"
        f"  actual:   {result['final_stage']}"
    )
