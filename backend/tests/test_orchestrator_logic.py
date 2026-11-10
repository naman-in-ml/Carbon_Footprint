from pipeline.orchestrator import _scale_estimate_for_truncated_aoi


def test_truncated_aoi_scales_carbon_estimate_to_claimed_area():
    estimate = {
        "estimated_tco2": 7_854.0,
        "low_estimate": 3_927.0,
        "high_estimate": 11_781.0,
    }

    result = _scale_estimate_for_truncated_aoi(
        estimate,
        claimed_hectares=20_000,
        aoi_hectares=7_854,
    )

    assert result["estimated_tco2"] == 20_000.0
    assert result["low_estimate"] == 10_000.0
    assert result["high_estimate"] == 30_000.0
