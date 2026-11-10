import pytest

from services.allometric import estimate_tco2, ndvi_to_canopy_fraction, reconcile_credits


def test_estimate_dense_canopy():
    expected = 100 * 120 * 1.0 * 0.475 * (44 / 12) * 1.25
    assert estimate_tco2(100, 0.6, "teak")["estimated_tco2"] == pytest.approx(expected, rel=1e-3)


def test_estimate_sparse_canopy():
    expected = 100 * 120 * 0.30 * 0.475 * (44 / 12) * 1.25
    assert estimate_tco2(100, 0.25, "teak")["estimated_tco2"] == pytest.approx(expected, rel=1e-3)


def test_satellite_area_does_not_double_discount():
    expected = 100 * 120 * 1.0 * 0.475 * (44 / 12) * 1.25
    result = estimate_tco2(100, 0.25, "teak", apply_canopy_fraction=False)
    assert result["estimated_tco2"] == pytest.approx(expected, rel=1e-3)
    assert result["area_basis"] == "satellite_tree_cover"


def test_unknown_species_uses_default():
    expected = 100 * 90 * 1.0 * 0.475 * (44 / 12) * 1.25
    assert estimate_tco2(100, 0.6, "oak")["estimated_tco2"] == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize(("ndvi", "fraction"), [(None, 0.0), (0.5, 1.0), (0.35, 0.6), (0.2, 0.3), (0.1, 0.0)])
def test_canopy_fraction(ndvi, fraction):
    assert ndvi_to_canopy_fraction(ndvi) == fraction


@pytest.mark.parametrize(("claimed", "estimated", "flag"), [(100, 100, "ok"), (300, 100, "major_discrepancy"), (170, 100, "over_claimed"), (100, 150, "under_claimed")])
def test_reconcile(claimed, estimated, flag):
    assert reconcile_credits(claimed, estimated)["credit_flag"] == flag
