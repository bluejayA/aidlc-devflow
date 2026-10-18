"""Unit tests for routing engine helper functions.

Tests individual engine functions in isolation to enable
precise failure diagnosis beyond integration-level scenarios.
"""

import pytest

from routing_engine import (
    _associate_conditions,
    _eval_condition,
    _find_step_index,
    _process_gate,
    _resolve_choice,
    simulate,
)


# --- _eval_condition ---


class TestEvalCondition:
    """Test condition expression evaluation."""

    def test_simple_match(self):
        cond = {"expr": "complexity==Minimal", "target": "workflow-planning"}
        assert _eval_condition(cond, "Minimal") == "workflow-planning"

    def test_simple_no_match(self):
        cond = {"expr": "complexity==Minimal", "target": "workflow-planning"}
        assert _eval_condition(cond, "Standard") is None

    def test_compound_all_match(self):
        cond = {"expr": "complexity==Comprehensive,application-design==included", "target": "app-design"}
        # Only complexity is evaluated by the engine; other keys pass through
        assert _eval_condition(cond, "Comprehensive") == "app-design"

    def test_compound_complexity_mismatch(self):
        cond = {"expr": "complexity==Comprehensive,application-design==included", "target": "app-design"}
        assert _eval_condition(cond, "Minimal") is None

    def test_no_equals_operator(self):
        cond = {"expr": "some-flag", "target": "somewhere"}
        assert _eval_condition(cond, "Standard") is None

    def test_empty_expr(self):
        cond = {"expr": "", "target": "somewhere"}
        assert _eval_condition(cond, "Standard") is None

    def test_compound_part_missing_equals(self):
        cond = {"expr": "complexity==Standard,no-equals-here", "target": "somewhere"}
        assert _eval_condition(cond, "Standard") is None


# --- _resolve_choice ---


class TestResolveChoice:
    """Test gate choice resolution."""

    def test_found(self):
        gate = {"id": "g1", "options": [
            {"option": "A", "target": "step-a"},
            {"option": "B", "target": "step-b"},
        ]}
        assert _resolve_choice(gate, "A") == "step-a"
        assert _resolve_choice(gate, "B") == "step-b"

    def test_not_found(self):
        gate = {"id": "g1", "options": [
            {"option": "A", "target": "step-a"},
        ]}
        assert _resolve_choice(gate, "C") is None

    def test_empty_options(self):
        gate = {"id": "g1", "options": []}
        assert _resolve_choice(gate, "A") is None


# --- _find_step_index ---


class TestFindStepIndex:
    """Test step index lookup."""

    def test_found(self):
        steps = [{"id": "s1", "order": 1}, {"id": "s2", "order": 2}]
        assert _find_step_index(steps, "s2") == 1

    def test_not_found(self):
        steps = [{"id": "s1", "order": 1}]
        assert _find_step_index(steps, "missing") is None

    def test_empty_list(self):
        assert _find_step_index([], "s1") is None


# --- _associate_conditions ---


class TestAssociateConditions:
    """Test condition-to-gate association."""

    def test_associates_by_shared_target(self):
        gates_by_id = {
            "g1": {"id": "g1", "options": [
                {"option": "A", "target": "step-a"},
                {"option": "B", "target": "step-b"},
            ]},
        }
        conditions = [{"expr": "complexity==Minimal", "target": "step-a"}]
        result = _associate_conditions(gates_by_id, conditions)
        assert "g1" in result
        assert len(result["g1"]) == 1

    def test_no_match(self):
        gates_by_id = {
            "g1": {"id": "g1", "options": [
                {"option": "A", "target": "step-a"},
            ]},
        }
        conditions = [{"expr": "complexity==Minimal", "target": "unrelated"}]
        result = _associate_conditions(gates_by_id, conditions)
        assert result == {}

    def test_empty_conditions(self):
        gates_by_id = {"g1": {"id": "g1", "options": [{"option": "A", "target": "x"}]}}
        result = _associate_conditions(gates_by_id, [])
        assert result == {}


# --- _process_gate ---


class TestProcessGate:
    """Test gate processing logic."""

    def _make_context(self):
        """Create minimal gate context for testing."""
        gates_by_id = {
            "g1": {"id": "g1", "options": [
                {"option": "A", "target": "step-a"},
                {"option": "B", "target": "step-b"},
            ]},
        }
        return gates_by_id

    def test_choice_resolves(self):
        gates = self._make_context()
        result = _process_gate("g1", gates, {}, {"g1": "A"}, "Standard")
        assert result == "step-a"

    def test_no_choice_returns_none(self):
        gates = self._make_context()
        result = _process_gate("g1", gates, {}, {}, "Standard")
        assert result is None

    def test_condition_takes_precedence(self):
        gates = self._make_context()
        cond_by_gate = {"g1": [{"expr": "complexity==Minimal", "target": "step-a"}]}
        result = _process_gate("g1", gates, cond_by_gate, {"g1": "B"}, "Minimal")
        assert result == "step-a"  # condition wins over choice

    def test_condition_no_match_falls_to_choice(self):
        gates = self._make_context()
        cond_by_gate = {"g1": [{"expr": "complexity==Minimal", "target": "step-a"}]}
        result = _process_gate("g1", gates, cond_by_gate, {"g1": "B"}, "Standard")
        assert result == "step-b"  # condition fails, choice used

    def test_self_ref_returns_next(self):
        gates_by_id = {
            "g1": {"id": "g1", "options": [
                {"option": "A", "target": "g1"},  # self-reference
                {"option": "B", "target": "step-b"},
            ]},
        }
        result = _process_gate("g1", gates_by_id, {}, {"g1": "A"}, "Standard")
        assert result == "__next__"

    def test_unknown_choice_stops(self):
        """Unknown choice (e.g. interrupt) should stop, not continue."""
        gates = self._make_context()
        result = _process_gate("g1", gates, {}, {"g1": "Z"}, "Standard")
        assert result is None


# --- simulate (edge cases) ---


class TestSimulateEdgeCases:
    """Test simulate function edge cases not covered by YAML scenarios."""

    def test_empty_graph(self):
        graph = {"steps": [], "gates": [], "conditions": []}
        result = simulate(graph, {})
        assert result["stage_path"] == []
        assert result["final_stage"] is None

    def test_single_step_no_gate(self):
        graph = {
            "steps": [{"id": "only-step", "order": 1}],
            "gates": [],
            "conditions": [],
        }
        result = simulate(graph, {})
        assert result["stage_path"] == ["only-step"]
        assert result["final_stage"] == "only-step"

    def test_skip_when_matches(self):
        graph = {
            "steps": [
                {"id": "s1", "order": 1},
                {"id": "s2", "order": 2, "skipWhen": "Minimal"},
                {"id": "s3", "order": 3},
            ],
            "gates": [],
            "conditions": [],
        }
        result = simulate(graph, {"complexity": "Minimal"})
        assert result["stage_path"] == ["s1", "s3"]

    def test_skip_when_no_match(self):
        graph = {
            "steps": [
                {"id": "s1", "order": 1},
                {"id": "s2", "order": 2, "skipWhen": "Minimal"},
                {"id": "s3", "order": 3},
            ],
            "gates": [],
            "conditions": [],
        }
        result = simulate(graph, {"complexity": "Standard"})
        assert result["stage_path"] == ["s1", "s2", "s3"]
