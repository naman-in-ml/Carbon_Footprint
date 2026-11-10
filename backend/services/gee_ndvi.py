"""Stage 2 NDVI verification over a boundary or claim-sized circle.

The control is a same-sized offset region. This is a screening heuristic: its
soil and land use may differ from the project area.
"""
import ee

from services._gee_init import init_gee
from services.gee_common import mean_ndvi


def classify_planting(
    ndvi_before: float | None,
    ndvi_after_3yr: float | None,
    control_before: float | None,
    control_after_3yr: float | None,
) -> dict:
    """Classify planting using project-versus-control difference-in-differences."""
    if (
        ndvi_before is None
        or ndvi_after_3yr is None
        or control_before is None
        or control_after_3yr is None
    ):
        return {
            "planting_verified": "unknown",
            "planting_confidence": 0.3,
            "ndvi_trend": "unknown",
        }
    net_gain = (ndvi_after_3yr - ndvi_before) - (
        control_after_3yr - control_before
    )
    if net_gain > 0.15:
        return {
            "planting_verified": "yes",
            "planting_confidence": min(0.5 + net_gain, 0.95),
            "ndvi_trend": "rising",
        }
    if net_gain > 0.05:
        return {
            "planting_verified": "partial",
            "planting_confidence": 0.4,
            "ndvi_trend": "rising",
        }
    return {
        "planting_verified": "no",
        "planting_confidence": 0.2,
        "ndvi_trend": "flat",
    }


def _clean_ndvi(value: float | None) -> float | None:
    if value is None or value < -0.5:
        return None
    return round(value, 4)


def compute_ndvi_stats(aoi: ee.Geometry, control: ee.Geometry, start_year: int) -> dict:
    """NDVI before planting, one and three years after, plus an offset control."""
    init_gee()
    try:
        values = ee.Dictionary(
            {
                "before": mean_ndvi(aoi, start_year - 1),
                "after_1yr": mean_ndvi(aoi, start_year + 1),
                "after_3yr": mean_ndvi(aoi, start_year + 3),
                "control_before": mean_ndvi(control, start_year - 1),
                "control_after_3yr": mean_ndvi(control, start_year + 3),
            }
        ).getInfo()
        before = _clean_ndvi(values.get("before"))
        after_1yr = _clean_ndvi(values.get("after_1yr"))
        after_3yr = _clean_ndvi(values.get("after_3yr"))
        control_before = _clean_ndvi(values.get("control_before"))
        control_after_3yr = _clean_ndvi(values.get("control_after_3yr"))
        classification = classify_planting(
            before, after_3yr, control_before, control_after_3yr
        )
        return {
            "ndvi_before": before,
            "ndvi_after_1yr": after_1yr,
            "ndvi_after_3yr": after_3yr,
            "ndvi_control": control_after_3yr,
            "ndvi_control_before": control_before,
            **classification,
            "control_method": "same_sized_offset_buffer",
            "control_limitation": (
                "Control is a spatially separate buffer; land-use similarity "
                "to the project area is not guaranteed."
            ),
        }
    except Exception as exc:
        return {"error": str(exc), "planting_verified": "unknown"}
