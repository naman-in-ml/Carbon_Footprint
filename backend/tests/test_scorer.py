from services.scorer import (
    area_ratio,
    compute_composite,
    loss_fraction,
    map_credit_flag_to_risk,
    score_permanence,
)

BASE = dict(
    extraction_confidence=0.9,
    requires_review=False,
    planting_verified="yes",
    planting_confidence=0.8,
    still_standing="yes",
    fire_events_detected=0,
    decline_detected=False,
    credit_flag="ok",
)


def test_healthy_project_is_low_risk():
    result = compute_composite(**BASE)
    assert result["risk_flag"] == "low"
    assert result["flag_reasons"] == {}


def test_area_shortfall_caps_planting():
    result = compute_composite(**BASE, claimed_hectares=1000, tree_cover_ha=200)
    assert result["planting_score"] <= 40
    assert "area" in result["flag_reasons"]


def test_good_area_has_no_flag():
    result = compute_composite(**BASE, claimed_hectares=1000, tree_cover_ha=900)
    assert "area" not in result["flag_reasons"]


def test_truncated_aoi_uses_effective_area_without_area_shortfall():
    result = compute_composite(
        **BASE,
        claimed_hectares=20_000,
        aoi_ha=7_854,
        tree_cover_ha=7_854,
    )
    assert result["planting_score"] > 40
    assert "area" not in result["flag_reasons"]
    assert "aoi_truncated" in result["flag_reasons"]


def test_forest_loss_caps_permanence():
    result = compute_composite(**BASE, tree_cover_ha=500, forest_loss_ha=200)
    assert result["permanence_score"] <= 50
    assert "forest_loss" in result["flag_reasons"]


def test_one_fire_day_does_not_cap_permanence():
    assert score_permanence("yes", fire_events=1, decline_detected=False) == 95


def test_three_fire_days_cap_permanence():
    assert score_permanence("yes", fire_events=3, decline_detected=False) == 50


def test_multiple_failures_are_critical():
    result = compute_composite(**{**BASE, "planting_verified": "no", "planting_confidence": 0.2, "still_standing": "no", "credit_flag": "major_discrepancy"})
    assert result["risk_flag"] == "critical"


def test_phantom_forest_is_critical():
    result = compute_composite(**{**BASE, "planting_verified": "no", "planting_confidence": 0.2, "credit_flag": "major_discrepancy"})
    assert result["risk_flag"] == "critical"
    assert "planting_absent" in result["flag_reasons"]


def test_area_ratio_edges():
    assert area_ratio(None, 10) is None
    assert area_ratio(0, 10) is None
    assert area_ratio(100, 150) == 1.0
    assert area_ratio(20_000, 7_854, 7_854) == 1.0


def test_loss_fraction_edges():
    assert loss_fraction(None, 100) == 0.0
    assert loss_fraction(25, 75) == 0.25


def test_credit_risk_mapping():
    assert map_credit_flag_to_risk("major_discrepancy") == "critical"
    assert map_credit_flag_to_risk(None) == "low"
