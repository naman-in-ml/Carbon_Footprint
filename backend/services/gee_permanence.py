"""Stage 3: permanence check — NDVI time series + NASA FIRMS fire events."""
import csv
import io
from datetime import datetime

import httpx
import ee

from core.config import settings
from services._gee_init import init_gee


def compute_ndvi_time_series(lat: float, lon: float, start_year: int, buffer_m: int = 5000) -> dict:
    init_gee()
    point = ee.Geometry.Point([lon, lat])
    polygon = point.buffer(buffer_m)
    current_year = datetime.utcnow().year
    years = list(range(start_year, current_year + 1))

    time_series = {}
    for year in years:
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(polygon)
            .filterDate(f"{year}-01-01", f"{year}-12-31")
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
            .map(lambda img: img.normalizedDifference(["B8", "B4"]).rename("NDVI"))
        )
        mean_image = collection.mean()
        stats = mean_image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=polygon,
            scale=10,
            maxPixels=1e9,
        ).getInfo()
        time_series[str(year)] = round(stats.get("NDVI") or 0, 4)

    ndvi_values = list(time_series.values())
    years_list = list(time_series.keys())

    decline_year = None
    for i in range(1, len(ndvi_values)):
        if (ndvi_values[i - 1] or 0) - (ndvi_values[i] or 0) > 0.10:
            decline_year = years_list[i]
            break

    current_ndvi = ndvi_values[-1] if ndvi_values else None
    still_standing = "yes"
    if decline_year:
        still_standing = "no" if (current_ndvi < 0.25) else "partial"

    return {
        "ndvi_time_series": time_series,
        "ndvi_current": current_ndvi,
        "still_standing": still_standing,
        "decline_detected_since": decline_year,
    }


async def check_fire_events(lat: float, lon: float, start_year: int) -> dict:
    end_date = datetime.utcnow().strftime("%Y-%m-%d")
    url = (
        f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
        f"{settings.firms_map_key}/VIIRS_SNPP_NRT/"
        f"{lon - 0.1},{lat - 0.1},{lon + 0.1},{lat + 0.1}/1/{end_date}"
    )
    fire_events = []
    if not settings.firms_map_key:
        return {"fire_events_detected": 0, "fire_dates": [], "likely_cause": "unclear"}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url)
            if resp.status_code == 200 and resp.text.strip():
                # csv.DictReader — the CSV contains quoted fields with commas.
                reader = csv.DictReader(io.StringIO(resp.text))
                for row in reader:
                    fire_events.append(
                        {
                            "date": row.get("acq_date"),
                            "confidence": row.get("confidence"),
                            "frp": row.get("frp"),
                        }
                    )
    except Exception:
        pass
    return {
        "fire_events_detected": len(fire_events),
        "fire_dates": [e["date"] for e in fire_events],
        "likely_cause": "fire" if fire_events else "unclear",
    }