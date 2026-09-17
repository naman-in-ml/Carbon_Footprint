"""Week-one GEE smoke test. Run before writing anything else.

    python scripts/gee_smoke_test.py

If it prints a number, the geospatial track is unblocked.
"""
import ee

ee.Initialize()

lat, lon = 11.4, 76.7  # Nilgiri Hills, Tamil Nadu
point = ee.Geometry.Point([lon, lat])
polygon = point.buffer(5000)

collection = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(polygon)
    .filterDate("2023-01-01", "2023-12-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    .map(lambda img: img.normalizedDifference(["B8", "B4"]).rename("NDVI"))
)

result = collection.mean().reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=polygon,
    scale=10,
    maxPixels=1e9,
).getInfo()

print(f"NDVI for Nilgiris 2023: {result.get('NDVI'):.4f}")
# Expected: ~0.55-0.75 (dense forest)