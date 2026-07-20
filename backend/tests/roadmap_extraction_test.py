"""Unit tests for roadmap extraction parsing logic (no DB / network needed)."""

from app.services.roadmap_extraction import (
    _parse_roadmap_from_response,
    _normalise_node_type,
    _parse_deadline,
)


def test_parse_valid_roadmap():
    payload = (
        '{"nodes": ['
        '{"title": "Midterm Exam", "node_type": "Exam", "deadline": "2026-10-15", "weight_percent": 30, "confidence": 0.9},'
        '{"title": "Homework 1", "node_type": "Assignment", "deadline": null, "weight_percent": 10, "confidence": 0.6}'
        '], "warnings": ["No final date found"]}'
    )
    nodes, warnings = _parse_roadmap_from_response(payload)
    assert len(nodes) == 2
    assert warnings == ["No final date found"]

    n0 = nodes[0]
    assert n0["title"] == "Midterm Exam"
    assert n0["node_type"] == "Exam"
    assert n0["deadline"].year == 2026
    assert n0["weight_percent"] == 30
    assert n0["extraction_confidence"] == 0.9
    assert n0["is_placeholder"] is False  # both fields present

    n1 = nodes[1]
    assert n1["deadline"] is None
    assert n1["is_placeholder"] is True  # missing deadline → placeholder


def test_parse_strips_markdown_fences():
    payload = '```json\n{"nodes": [{"title": "Quiz 1", "node_type": "quiz"}], "warnings": []}\n```'
    nodes, _ = _parse_roadmap_from_response(payload)
    assert len(nodes) == 1
    assert nodes[0]["title"] == "Quiz 1"


def test_parse_empty_nodes():
    nodes, warnings = _parse_roadmap_from_response('{"nodes": [], "warnings": ["nothing found"]}')
    assert nodes == []
    assert warnings == ["nothing found"]


def test_parse_invalid_json():
    nodes, warnings = _parse_roadmap_from_response("not json at all")
    assert nodes == []
    assert warnings  # some warning returned


def test_parse_skips_items_without_title():
    payload = '{"nodes": [{"node_type": "Exam"}, {"title": "Real", "node_type": "Exam"}], "warnings": []}'
    nodes, _ = _parse_roadmap_from_response(payload)
    assert len(nodes) == 1
    assert nodes[0]["title"] == "Real"


def test_node_type_normalisation():
    assert _normalise_node_type("exam") == "Exam"
    assert _normalise_node_type("Midterm") == "Exam"
    assert _normalise_node_type("lab report") == "Lab"
    assert _normalise_node_type("project") == "Project"
    assert _normalise_node_type("") == "Other"
    assert _normalise_node_type("Banana") == "Other"


def test_node_type_passthrough_canonical():
    for t in ["Assignment", "Quiz", "Exam", "Project", "Lab", "Other"]:
        assert _normalise_node_type(t) == t


def test_deadline_parsing():
    assert _parse_deadline("2026-12-01").year == 2026
    # datetime with Z
    dt = _parse_deadline("2026-12-01T15:30:00Z")
    assert dt.year == 2026 and dt.tzinfo is not None
    # invalid → None
    assert _parse_deadline("soon") is None
    assert _parse_deadline("") is None
    assert _parse_deadline(None) is None


def test_confidence_clamped():
    payload = '{"nodes": [{"title": "X", "node_type": "Exam", "confidence": 5.0}], "warnings": []}'
    nodes, _ = _parse_roadmap_from_response(payload)
    assert nodes[0]["extraction_confidence"] == 1.0
