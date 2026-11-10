"""Shared Earth Engine helpers: analysis area, cloud-masked NDVI."""
import math

import ee

from services._gee_init import init_gee
from services.geometry import buffer_radius_m, geometry_area_ha

S2_COLLECTION = "COPERNICUS/S2_SR_HARMONIZED"
# Sentinel-2 Scene Classification: 3=cloud shadow, 8/9=cloud, 10=cirrus.
_SCL_MASKED = (3, 8, 9, 10)
CONTROL_OFFSET_DEG = (0.1, 0.2)  # (lat, lon) offset of the control region


def build_aoi(
    lat: float,
    lon: float,
    claimed_hectares: float | None,
    boundary_geojson: dict | None = None,
) -> tuple[ee.Geometry, int]:
    """Return (analysis geometry, equivalent radius in metres)."""
    init_gee()
    if boundary_geojson:
        radius = max(
            int(math.sqrt(geometry_area_ha(boundary_geojson) * 10_000 / math.pi)), 1
        )
        return ee.Geometry(boundary_geojson), radius
    radius = buffer_radius_m(claimed_hectares)
    return ee.Geometry.Point([lon, lat]).buffer(radius), radius


def build_control(lat: float, lon: float, radius_m: int) -> ee.Geometry:
    """Same-sized region offset from the project (screening heuristic)."""
    return ee.Geometry.Point(
        [lon + CONTROL_OFFSET_DEG[1], lat + CONTROL_OFFSET_DEG[0]]
    ).buffer(radius_m)


def _mask_clouds(img: ee.Image) -> ee.Image:
    scl = img.select("SCL")
    mask = scl.neq(_SCL_MASKED[0])
    for cloud_class in _SCL_MASKED[1:]:
        mask = mask.And(scl.neq(cloud_class))
    return img.updateMask(mask)


def mean_ndvi(geometry: ee.Geometry, year: int) -> ee.Number:
    """Server-side median-composite NDVI for a year. -1 when there is no imagery."""
    composite = (
        ee.ImageCollection(S2_COLLECTION)
        .filterBounds(geometry)
        .filterDate(f"{year}-01-01", f"{year}-12-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
        .map(_mask_clouds)
        .map(lambda img: img.normalizedDifference(["B8", "B4"]).rename("NDVI"))
        .median()
    )
    stats = composite.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=10,
        maxPixels=1e10,
        bestEffort=True,
    )
    return ee.Dictionary(stats).get("NDVI", -1)
