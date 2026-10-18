"""Routing simulation engine for orchestrator JSON graphs.

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


def simulate(graph: dict, inputs: dict) -> dict:
    """Simulate orchestrator routing on a JSON graph."""
    complexity = inputs.get("complexity", "Standard")
    choices = inputs.get("choices", {})

    steps = sorted(graph["steps"], key=lambda s: s["order"])
    gates_by_id = {g["id"]: g for g in graph["gates"]}

    cond_by_gate = _associate_conditions(gates_by_id, graph.get("conditions", []))

    stage_path = []

    i = 0
    safety = 0

    while i < len(steps) and safety < 200:
        safety += 1
        step = steps[i]
        step_id = step["id"]

        if step.get("skipWhen") and step["skipWhen"] == complexity:
            i += 1
            continue

        stage_path.append(step_id)

        if step_id in gates_by_id:
            jump = _process_gate(step_id, gates_by_id, cond_by_gate, choices, complexity)
            if jump is None:
                break
            if jump != "__next__":
                target_idx = _find_step_index(steps, jump)
                if target_idx is not None:
                    i = target_idx
                    continue
                break

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
                    continue
                target_idx = _find_step_index(steps, jump)
                if target_idx is not None:
                    i = target_idx
                    should_jump = True
                    break
                should_stop = True
                break
            if should_stop:
                break
            if should_jump:
                continue

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
    for cond in cond_by_gate.get(gate_id, []):
        result = _eval_condition(cond, complexity)
        if result:
            return result

    choice = choices.get(gate_id)
    if choice is None:
        return None

    gate = gates_by_id[gate_id]
    target = _resolve_choice(gate, choice)
    if target is None:
        return None  # Unknown choice = stop (interrupt handler at SKILL.md level)
    if target == gate_id:
        return "__next__"
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
