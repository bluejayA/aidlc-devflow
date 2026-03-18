"""Parser output validation tests.

Validates that parse-skills.js correctly extracts meta tags
from SKILL.md files and produces valid JSON graphs.
"""

import subprocess
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent
SKILLS_DIR = TESTS_DIR.parent / "skills"


@pytest.fixture(scope="session", autouse=True)
def run_parser():
    """Run parse-skills.js once before all tests in this module."""
    result = subprocess.run(
        ["node", str(TESTS_DIR / "parse-skills.js")],
        capture_output=True,
        text=True,
        cwd=TESTS_DIR.parent,
    )
    if result.returncode != 0:
        pytest.fail(f"parse-skills.js failed:\n{result.stderr}")


class TestParserGeneratesJson:
    """Verify parser creates JSON graph files."""

    def test_inception_json_exists(self, load_graph):
        # load_graph raises FileNotFoundError if missing
        load_graph("aidlc-inception-orchestrator")

    def test_construction_json_exists(self, load_graph):
        load_graph("aidlc-construction-orchestrator")


class TestParserJsonSchema:
    """Verify JSON graph files have the correct schema."""

    def test_inception_has_required_keys(self, load_graph):
        graph = load_graph("aidlc-inception-orchestrator")
        for key in ("name", "steps", "gates", "conditions"):
            assert key in graph, f"Missing key: {key}"

    def test_construction_has_required_keys(self, load_graph):
        graph = load_graph("aidlc-construction-orchestrator")
        for key in ("name", "steps", "gates", "conditions"):
            assert key in graph, f"Missing key: {key}"

    def test_inception_name(self, load_graph):
        graph = load_graph("aidlc-inception-orchestrator")
        assert graph["name"] == "aidlc-inception-orchestrator"

    def test_construction_name(self, load_graph):
        graph = load_graph("aidlc-construction-orchestrator")
        assert graph["name"] == "aidlc-construction-orchestrator"


class TestParserInceptionContent:
    """Verify inception-orchestrator JSON has correct content."""

    def test_steps_count(self, load_graph):
        graph = load_graph("aidlc-inception-orchestrator")
        assert len(graph["steps"]) >= 8, (
            f"Expected >= 8 steps, got {len(graph['steps'])}"
        )

    def test_first_step_is_workspace_detection(self, load_graph):
        graph = load_graph("aidlc-inception-orchestrator")
        assert graph["steps"][0]["id"] == "workspace-detection"

    def test_steps_have_order_and_id(self, load_graph):
        graph = load_graph("aidlc-inception-orchestrator")
        for step in graph["steps"]:
            assert "order" in step, f"Step missing 'order': {step}"
            assert "id" in step, f"Step missing 'id': {step}"

    def test_gates_count(self, load_graph):
        graph = load_graph("aidlc-inception-orchestrator")
        assert len(graph["gates"]) >= 2, (
            f"Expected >= 2 gates, got {len(graph['gates'])}"
        )

    def test_gate_has_id_and_options(self, load_graph):
        graph = load_graph("aidlc-inception-orchestrator")
        for gate in graph["gates"]:
            assert "id" in gate, f"Gate missing 'id': {gate}"
            assert "options" in gate, f"Gate missing 'options': {gate}"
            assert len(gate["options"]) >= 2, (
                f"Gate '{gate['id']}' has < 2 options"
            )

    def test_gate_option_has_target(self, load_graph):
        graph = load_graph("aidlc-inception-orchestrator")
        for gate in graph["gates"]:
            for opt in gate["options"]:
                assert "option" in opt, f"Option missing 'option' in gate '{gate['id']}'"
                assert "target" in opt, f"Option missing 'target' in gate '{gate['id']}'"

    def test_conditions_count(self, load_graph):
        graph = load_graph("aidlc-inception-orchestrator")
        assert len(graph["conditions"]) >= 1, (
            f"Expected >= 1 conditions, got {len(graph['conditions'])}"
        )

    def test_condition_has_expr_and_target(self, load_graph):
        graph = load_graph("aidlc-inception-orchestrator")
        for cond in graph["conditions"]:
            assert "expr" in cond, f"Condition missing 'expr': {cond}"
            assert "target" in cond, f"Condition missing 'target': {cond}"
