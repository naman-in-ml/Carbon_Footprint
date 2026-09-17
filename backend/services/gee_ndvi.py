"""Stage 2: NDVI planting verification on Google Earth Engine.

Control region: we compare against a *spatially separate* buffer placed
~CONTROL_OFFSET_M away from the project, not an annulus ring around it
(a project surrounded by similar land would create a false "no difference").
This is still a screening heuristic — the control region may differ in soil or
land use, which we flag as a limitation in the returned metadata.
"""
import ee

from services._gee_init import init_gee

CONTROL_OFFSET_M = 15000


def compute_ndvi_stats(lat: float, lon: float, start_year: int, buffer_m: int = 5000) -> dict:
    """NDVI before planting, 1 yr after, 3 yr after, plus a separate control region."""
    init_gee()
    point = ee.Geometry.Point([lon, lat])
    polygon = point.buffer(buffer_m)
    # A separate, similar-sized region offset from the project boundary.
    control_point = ee.Geometry.Point([lon + 0.2, lat + 0.1]).buffer(buffer_m)

    def get_mean_ndvi(geometry, year: int):
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(geometry)
            .filterDate(f"{year}-01-01", f"{year}-12-31")
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
            .map(lambda img: img.normalizedDifference(["B8", "B4"]).rename("NDVI"))
        )
        mean_image = collection.mean()
        stats = mean_image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=10,
            maxPixels=1e9,
        )
        return stats.getInfo().get("NDVI")

    baseline_year = start_year - 1
    try:
        ndvi_before = get_mean_ndvi(polygon, baseline_year)
        ndvi_after_1yr = get_mean_ndvi(polygon, start_year + 1)
        ndvi_after_3yr = get_mean_ndvi(polygon, start_year + 3)
        ndvi_control = get_mean_ndvi(control_point, start_year + 1)
    except Exception as exc:
        return {"error": str(exc), "planting_verified": "unknown"}

    delta = (ndvi_after_3yr or 0) - (ndvi_before or 0)
    control_delta = (ndvi_control or 0) - (ndvi_before or 0)
    net_gain = delta - control_delta

    if net_gain > 0.15:
        planting_verified = "yes"
        planting_confidence = min(0.5 + net_gain, 0.95)
        ndvi_trend = "rising"
    elif net_gain > 0.05:
        planting_verified = "partial"
        planting_confidence = 0.4
        ndvi_trend = "rising"
    else:
        planting_verified = "no"
        planting_confidence = 0.2
        ndvi_trend = "flat"

    return {
        "ndvi_before": round(ndvi_before or 0, 4),
        "ndvi_after_1yr": round(ndvi_after_1yr or 0, 4),
        "ndvi_after_3yr": round(ndvi_after_3yr or 0, 4),
        "ndvi_control": round(ndvi_control or 0, 4),
        "ndvi_trend": ndvi_trend,
        "planting_verified": planting_verified,
        "planting_confidence": round(planting_confidence, 2),
        "control_method": f"offset_buffer_{CONTROL_OFFSET_M}m",
        "control_limitation": (
            "Control is a spatially separate buffer; land-use similarity "
            "to the project area is not guaranteed."
        ),
    }