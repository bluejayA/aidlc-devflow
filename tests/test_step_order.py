"""L3 Step Order Checker — step sequence and required step validation.

Validates:
1. Step order numbers are strictly monotonically increasing
2. Required steps exist for each orchestrator
3. skip-when values reference valid modes
"""

import pytest

ORCHESTRATORS = [
    "aidlc-inception-orchestrator",
    "aidlc-construction-orchestrator",
]

# Required steps per orchestrator
REQUIRED_STEPS = {
    "aidlc-inception-orchestrator": [
        "workspace-detection",
        "complexity-declaration",
        "requirements-analysis",
        "workflow-planning",
    ],
    "aidlc-construction-orchestrator": [
        "context-load",
        "stage-decision",
    ],
}

# Valid skip-when modes (complexity levels + special modes)
VALID_SKIP_MODES = {
    "Minimal",
    "Standard",
    "Comprehensive",
    "no-completed-units",
    "QUESTIONS",
    "no-held-items",
}


@pytest.mark.parametrize("name", ORCHESTRATORS)
class TestStepOrderIncreasing:
    """Step order numbers must be strictly monotonically increasing."""

    def test_step_order(self, load_graph, name):
        graph = load_graph(name)
        orders = [s["order"] for s in graph["steps"]]
        assert len(orders) >= 2, f"Need at least 2 steps in {name}"
        for i in range(1, len(orders)):
            assert orders[i] > orders[i - 1], (
                f"Step order not increasing in {name} at position {i}: "
                f"{orders[i - 1]} -> {orders[i]}"
            )


class TestAllGraphsStepOrder:
    """Verify all graphs (not just orchestrators) have increasing order."""

    def test_all_graphs(self, load_all_graphs):
        graphs = load_all_graphs()
        for name, graph in graphs.items():
            orders = [s["order"] for s in graph["steps"]]
            for i in range(1, len(orders)):
                assert orders[i] > orders[i - 1], (
                    f"[{name}] Step order not increasing: "
                    f"{orders[i - 1]} -> {orders[i]}"
                )


@pytest.mark.parametrize("name", ORCHESTRATORS)
class TestRequiredStepsExist:
    """Each orchestrator must have its required steps."""

    def test_required_steps(self, load_graph, name):
        graph = load_graph(name)
        step_ids = {s["id"] for s in graph["steps"]}
        required = REQUIRED_STEPS[name]
        missing = [r for r in required if r not in step_ids]
        assert missing == [], f"Missing required steps in {name}: {missing}"


@pytest.mark.parametrize("name", ORCHESTRATORS)
class TestSkipRulesValid:
    """skip-when values must reference valid modes."""

    def test_skip_rules(self, load_graph, name):
        graph = load_graph(name)
        invalid = [
            f"step '{s['id']}' skip-when='{s['skipWhen']}'"
            for s in graph["steps"]
            if s.get("skipWhen") and s["skipWhen"] not in VALID_SKIP_MODES
        ]
        assert invalid == [], f"Invalid skip-when in {name}: {invalid}"


class TestAllGraphsSkipRules:
    """Verify all graphs have valid skip-when values."""

    def test_all_graphs(self, load_all_graphs):
        graphs = load_all_graphs()
        for name, graph in graphs.items():
            for step in graph["steps"]:
                sw = step.get("skipWhen")
                if sw:
                    assert sw in VALID_SKIP_MODES, (
                        f"[{name}] step '{step['id']}' has invalid skip-when='{sw}'"
                    )
