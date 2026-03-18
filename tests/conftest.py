"""Shared pytest fixtures for SKILL.md test infrastructure.

Provides fixtures for loading JSON graphs and YAML scenarios.
"""

import json
from pathlib import Path

import pytest
import yaml

TESTS_DIR = Path(__file__).parent
GRAPH_DIR = TESTS_DIR / "graph"
SCENARIOS_DIR = TESTS_DIR / "scenarios"


@pytest.fixture
def load_graph():
    """Factory fixture: load a single JSON graph by skill name."""

    def _load(name: str) -> dict:
        path = GRAPH_DIR / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Graph not found: {path}")
        return json.loads(path.read_text())

    return _load


@pytest.fixture
def load_all_graphs():
    """Factory fixture: load all JSON graphs from the graph directory."""

    def _load() -> dict[str, dict]:
        graphs = {}
        for path in sorted(GRAPH_DIR.glob("*.json")):
            data = json.loads(path.read_text())
            graphs[data["name"]] = data
        return graphs

    return _load


@pytest.fixture
def load_scenario():
    """Factory fixture: load a single YAML scenario by filename."""

    def _load(filename: str) -> dict:
        path = SCENARIOS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Scenario not found: {path}")
        return yaml.safe_load(path.read_text())

    return _load


@pytest.fixture
def all_scenarios():
    """Load all YAML scenarios from the scenarios directory."""
    if not SCENARIOS_DIR.exists():
        return []
    scenarios = []
    for path in sorted(SCENARIOS_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text())
        data["_file"] = path.name
        scenarios.append(data)
    return scenarios
