"""Verify conftest.py fixtures work correctly."""

from pathlib import Path


def test_load_graph_returns_dict(load_graph):
    graph = load_graph("aidlc-inception-orchestrator")
    assert isinstance(graph, dict)
    assert graph["name"] == "aidlc-inception-orchestrator"


def test_load_all_graphs_returns_multiple(load_all_graphs):
    graphs = load_all_graphs()
    assert len(graphs) >= 2
    assert "aidlc-inception-orchestrator" in graphs
    assert "aidlc-construction-orchestrator" in graphs


def test_load_graph_missing_raises(load_graph):
    import pytest

    with pytest.raises(FileNotFoundError):
        load_graph("nonexistent-skill")
