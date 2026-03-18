"""Parser output validation tests.

Validates that parse-skills.js correctly extracts meta tags
from SKILL.md files and produces valid JSON graphs.
"""

import json
import subprocess
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).parent
GRAPH_DIR = TESTS_DIR / "graph"
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

    def test_inception_json_exists(self):
        path = GRAPH_DIR / "aidlc-inception-orchestrator.json"
        assert path.exists(), f"Expected {path} to exist after parsing"

    def test_construction_json_exists(self):
        path = GRAPH_DIR / "aidlc-construction-orchestrator.json"
        assert path.exists(), f"Expected {path} to exist after parsing"


class TestParserJsonSchema:
    """Verify JSON graph files have the correct schema."""

    @pytest.fixture
    def inception_graph(self):
        path = GRAPH_DIR / "aidlc-inception-orchestrator.json"
        return json.loads(path.read_text())

    @pytest.fixture
    def construction_graph(self):
        path = GRAPH_DIR / "aidlc-construction-orchestrator.json"
        return json.loads(path.read_text())

    def test_inception_has_required_keys(self, inception_graph):
        for key in ("name", "steps", "gates", "conditions"):
            assert key in inception_graph, f"Missing key: {key}"

    def test_construction_has_required_keys(self, construction_graph):
        for key in ("name", "steps", "gates", "conditions"):
            assert key in construction_graph, f"Missing key: {key}"

    def test_inception_name(self, inception_graph):
        assert inception_graph["name"] == "aidlc-inception-orchestrator"

    def test_construction_name(self, construction_graph):
        assert construction_graph["name"] == "aidlc-construction-orchestrator"


class TestParserInceptionContent:
    """Verify inception-orchestrator JSON has correct content."""

    @pytest.fixture
    def graph(self):
        path = GRAPH_DIR / "aidlc-inception-orchestrator.json"
        return json.loads(path.read_text())

    def test_steps_count(self, graph):
        assert len(graph["steps"]) >= 8, (
            f"Expected >= 8 steps, got {len(graph['steps'])}"
        )

    def test_first_step_is_workspace_detection(self, graph):
        assert graph["steps"][0]["id"] == "workspace-detection"

    def test_steps_have_order_and_id(self, graph):
        for step in graph["steps"]:
            assert "order" in step, f"Step missing 'order': {step}"
            assert "id" in step, f"Step missing 'id': {step}"

    def test_gates_count(self, graph):
        assert len(graph["gates"]) >= 2, (
            f"Expected >= 2 gates, got {len(graph['gates'])}"
        )

    def test_gate_has_id_and_options(self, graph):
        for gate in graph["gates"]:
            assert "id" in gate, f"Gate missing 'id': {gate}"
            assert "options" in gate, f"Gate missing 'options': {gate}"
            assert len(gate["options"]) >= 2, (
                f"Gate '{gate['id']}' has < 2 options"
            )

    def test_gate_option_has_target(self, graph):
        for gate in graph["gates"]:
            for opt in gate["options"]:
                assert "option" in opt, f"Option missing 'option' in gate '{gate['id']}'"
                assert "target" in opt, f"Option missing 'target' in gate '{gate['id']}'"

    def test_conditions_count(self, graph):
        assert len(graph["conditions"]) >= 1, (
            f"Expected >= 1 conditions, got {len(graph['conditions'])}"
        )

    def test_condition_has_expr_and_target(self, graph):
        for cond in graph["conditions"]:
            assert "expr" in cond, f"Condition missing 'expr': {cond}"
            assert "target" in cond, f"Condition missing 'target': {cond}"
