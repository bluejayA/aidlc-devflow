"""L2 Routing Simulator — YAML fixture-based orchestrator simulation.

Simulates orchestrator routing on JSON graphs using deterministic
inputs (complexity, gate choices) and compares results to expected paths.

Simulation model:
- All nodes (steps and gates) are ordered by document position
- The simulator walks nodes sequentially
- Steps are always visited (unless skip-when matches)
- Gates require a choice or condition to proceed; missing choice = stop
- Gate target can jump to another node (step or gate)
- stage_path records all visited node IDs (steps and gates)
"""

import json
from pathlib import Path

import pytest
import yaml

TESTS_DIR = Path(__file__).parent
GRAPH_DIR = TESTS_DIR / "graph"
SCENARIOS_DIR = TESTS_DIR / "scenarios"


# --- Simulation Engine ---


def simulate(graph: dict, inputs: dict) -> dict:
    """Simulate orchestrator routing on a JSON graph."""
    complexity = inputs.get("complexity", "Standard")
    choices = inputs.get("choices", {})

    # Build ordered node list: interleave steps and gates by document order
    # Steps come first (they define the execution backbone), followed by
    # gates in document order. A gate that shares an id with a step is
    # "attached" to that step.
    steps = sorted(graph["steps"], key=lambda s: s["order"])
    gates_by_id = {g["id"]: g for g in graph["gates"]}
    step_ids = {s["id"] for s in steps}

    # Conditions associated with gates
    cond_by_gate = _associate_conditions(gates_by_id, graph.get("conditions", []))

    stage_path = []

    # Walk steps sequentially
    i = 0
    safety = 0

    while i < len(steps) and safety < 200:
        safety += 1
        step = steps[i]
        step_id = step["id"]

        # Skip if skip-when matches
        if step.get("skipWhen") and step["skipWhen"] == complexity:
            i += 1
            continue

        stage_path.append(step_id)

        # Process gate with same id (if exists)
        if step_id in gates_by_id:
            jump = _process_gate(step_id, gates_by_id, cond_by_gate, choices, complexity)
            if jump is None:
                break  # no choice — stop
            if jump != "__next__":
                target_idx = _find_step_index(steps, jump)
                if target_idx is not None:
                    i = target_idx
                    continue
                # Not a step — stop (external target)
                break

        # Check for sub-gates (gate ids that start with step_id + "-")
        sub_gates = [g for g in graph["gates"] if g["id"].startswith(step_id + "-")]
        if sub_gates:
            should_stop = False
            should_jump = False
            for sg in sub_gates:
                sg_id = sg["id"]
                jump = _process_gate(sg_id, gates_by_id, cond_by_gate, choices, complexity)
                if jump is None:
                    should_stop = True
                    break
                if jump == "__next__" or jump == step_id:
                    # __next__ = continue, step_id = skill invocation (not a jump)
                    continue
                target_idx = _find_step_index(steps, jump)
                if target_idx is not None:
                    i = target_idx
                    should_jump = True
                    break
                should_stop = True
                break
            if should_stop:
                break  # exit while loop
            if should_jump:
                continue  # jump to new step index

        i += 1

    return {
        "stage_path": stage_path,
        "final_stage": stage_path[-1] if stage_path else None,
    }


def _process_gate(
    gate_id: str, gates_by_id: dict, cond_by_gate: dict,
    choices: dict, complexity: str
) -> str | None:
    """Process a gate. Returns target id, "__next__" to continue, or None to stop."""
    # Check conditions first (auto-routing)
    for cond in cond_by_gate.get(gate_id, []):
        result = _eval_condition(cond, complexity)
        if result:
            return result

    # Use provided choice
    choice = choices.get(gate_id)
    if choice is None:
        return None  # stop

    gate = gates_by_id[gate_id]
    target = _resolve_choice(gate, choice)
    if target is None:
        return "__next__"
    if target == gate_id:
        return "__next__"  # self-ref = retry, continue
    return target


def _associate_conditions(
    gates_by_id: dict, conditions: list[dict]
) -> dict[str, list[dict]]:
    """Associate conditions with gates based on shared targets."""
    result: dict[str, list[dict]] = {}
    for cond in conditions:
        for gate_id, gate in gates_by_id.items():
            targets = {o["target"] for o in gate["options"]}
            if cond["target"] in targets:
                result.setdefault(gate_id, []).append(cond)
                break
    return result


def _eval_condition(cond: dict, complexity: str) -> str | None:
    """Evaluate a single condition expression."""
    expr = cond["expr"]
    if "==" not in expr:
        return None
    # Handle compound conditions: "a==X,b==Y"
    parts = [p.strip() for p in expr.split(",")]
    for part in parts:
        if "==" not in part:
            return None
        key, value = part.split("==", 1)
        if key.strip() == "complexity" and value.strip() != complexity:
            return None
    return cond["target"]


def _resolve_choice(gate: dict, choice: str) -> str | None:
    """Find the target for a given choice."""
    for opt in gate["options"]:
        if opt["option"] == choice:
            return opt["target"]
    return None


def _find_step_index(steps: list[dict], target_id: str) -> int | None:
    """Find step index by id."""
    for idx, step in enumerate(steps):
        if step["id"] == target_id:
            return idx
    return None


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
