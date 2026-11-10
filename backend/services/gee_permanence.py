"""Stage 3: permanence check — NDVI time series + NASA FIRMS fire events."""
from datetime import datetime

import ee

from services._gee_init import init_gee
from services.gee_common import mean_ndvi


def confidence_is_usable(value: str | int | float | None) -> bool:
    """Accept nominal/high categorical confidence or numeric confidence >= 50."""
    if isinstance(value, str):
        return value.lower() in {"n", "h"}
    if isinstance(value, bool) or value is None:
        return False
    return value >= 50


def classify_permanence(time_series: dict[str, float]) -> dict:
    """Classify whether vegetation remains from a pure NDVI time series."""
    years = list(time_series)
    values = list(time_series.values())
    current_ndvi = values[-1] if values else None
    if current_ndvi is None:
        return {
            "ndvi_current": None,
            "still_standing": "unknown",
            "decline_detected_since": None,
        }
    decline_year = None
    for index in range(1, len(values)):
        if values[index - 1] - values[index] > 0.10:
            decline_year = years[index]
            break
    still_standing = "yes"
    if decline_year:
        still_standing = "no" if current_ndvi < 0.25 else "partial"
    return {
        "ndvi_current": current_ndvi,
        "still_standing": still_standing,
        "decline_detected_since": decline_year,
    }


def compute_ndvi_time_series(aoi: ee.Geometry, start_year: int) -> dict:
    """Fetch one server-side dictionary for all annual NDVI values."""
    init_gee()
    current_year = datetime.utcnow().year
    years = range(start_year, current_year + 1)
    try:
        raw = ee.Dictionary(
            {str(year): mean_ndvi(aoi, year) for year in years}
        ).getInfo()
        time_series = {
            year: round(value, 4)
            for year, value in raw.items()
            if value is not None and value >= -0.5
        }
        return {"ndvi_time_series": time_series, **classify_permanence(time_series)}
    except Exception as exc:
        return {
            "ndvi_time_series": {},
            **classify_permanence({}),
            "error": str(exc),
        }


def check_fire_events(aoi: ee.Geometry, start_year: int) -> dict:
    """Distinct fire-detection days inside the AOI since project start (NASA FIRMS in GEE)."""
    init_gee()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    try:
        collection = (
            ee.ImageCollection("FIRMS")
            .filterBounds(aoi)
            .filterDate(f"{start_year}-01-01", today)
        )

        def image_to_feature(img):
            confident_fire = img.select("T21").updateMask(
                img.select("confidence").gte(50)
            )
            count = confident_fire.reduceRegion(
                ee.Reducer.count(),
                aoi,
                1000,
                maxPixels=1e9,
                bestEffort=True,
            ).get("T21")
            return ee.Feature(
                None,
                {"date": img.date().format("YYYY-MM-dd"), "n": count},
            )

        dates = (
            ee.FeatureCollection(collection.map(image_to_feature))
            .filter(ee.Filter.gt("n", 0))
            .aggregate_array("date")
            .getInfo()
        )
        unique_dates = sorted(set(dates))
        return {
            "fire_events_detected": len(unique_dates),
            "fire_dates": unique_dates,
            "likely_cause": "fire" if unique_dates else "unclear",
            "source": "NASA FIRMS (GEE)",
        }
    except Exception as exc:
        return {
            "fire_events_detected": 0,
            "fire_dates": [],
            "likely_cause": "unclear",
            "error": str(exc),
        }
