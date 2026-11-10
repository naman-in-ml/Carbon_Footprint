from services import gee_ndvi
from services.gee_ndvi import classify_planting
from services.gee_permanence import classify_permanence, confidence_is_usable


def test_planting_yes():
    assert classify_planting(0.30, 0.55, 0.30, 0.32)["planting_verified"] == "yes"


def test_planting_partial():
    assert classify_planting(0.30, 0.40, 0.30, 0.32)["planting_verified"] == "partial"


def test_planting_no():
    assert classify_planting(0.30, 0.32, 0.10, 0.10)["planting_verified"] == "no"


def test_planting_unknown():
    assert classify_planting(None, 0.5, 0.3, 0.3)["planting_verified"] == "unknown"


def test_compute_ndvi_stats_fetches_control_before_and_after(monkeypatch):
    calls = []

    class FakeDictionary(dict):
        def getInfo(self):
            return self

    def fake_mean_ndvi(geometry, year):
        calls.append((geometry, year))
        return {
            ("project", 2019): 0.30,
            ("project", 2021): 0.40,
            ("project", 2023): 0.55,
            ("control", 2019): 0.30,
            ("control", 2023): 0.32,
        }[(geometry, year)]

    monkeypatch.setattr(gee_ndvi, "init_gee", lambda: None)
    monkeypatch.setattr(gee_ndvi, "mean_ndvi", fake_mean_ndvi)
    monkeypatch.setattr(gee_ndvi.ee, "Dictionary", FakeDictionary)

    result = gee_ndvi.compute_ndvi_stats("project", "control", 2020)

    assert ("control", 2019) in calls
    assert ("control", 2023) in calls
    assert result["planting_verified"] == "yes"
    assert result["ndvi_control_before"] == 0.30
    assert result["ndvi_control"] == 0.32


def test_permanence_yes():
    result = classify_permanence({"2019": 0.4, "2020": 0.5, "2021": 0.6})
    assert result["still_standing"] == "yes"
    assert result["decline_detected_since"] is None


def test_permanence_no():
    result = classify_permanence({"2019": 0.7, "2020": 0.72, "2021": 0.5, "2022": 0.2})
    assert result["decline_detected_since"] == "2021"
    assert result["still_standing"] == "no"


def test_permanence_partial():
    result = classify_permanence({"2019": 0.7, "2020": 0.55, "2021": 0.5})
    assert result["decline_detected_since"] == "2020"
    assert result["still_standing"] == "partial"


def test_permanence_unknown():
    result = classify_permanence({})
    assert result["still_standing"] == "unknown"
    assert result["ndvi_current"] is None


def test_firms_confidence_filter_accepts_named_and_numeric_confidence():
    assert confidence_is_usable("n")
    assert confidence_is_usable("h")
    assert confidence_is_usable(50)
    assert confidence_is_usable(87)
    assert not confidence_is_usable("l")
    assert not confidence_is_usable(49)
    assert not confidence_is_usable(None)
