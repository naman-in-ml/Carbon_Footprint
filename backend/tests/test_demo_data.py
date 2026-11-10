import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from demo_projects import build_all


def test_demo_data_shape_and_names():
    records = build_all()
    assert len(records) == 4
    for record in records:
        assert record["claim"]["geometry_wkt"].startswith("POINT(")
        assert record["verification"]["tree_cover_ha"] is not None
        assert "(Demo)" in record["project"]["name"]


def test_phantom_forest_is_critical():
    record = build_all()[2]
    assert record["project"]["verra_id"] == "DEMO-ARR-003"
    assert record["score"]["risk_flag"] == "critical"
    assert "area" in record["score"]["flag_reasons"]


def test_healthy_project_is_low_risk():
    assert build_all()[0]["score"]["risk_flag"] == "low"


def test_fire_and_forest_loss_are_flagged():
    record = build_all()[3]
    assert record["verification"]["fire_events_detected"] == 4
    assert "forest_loss" in record["score"]["flag_reasons"]
