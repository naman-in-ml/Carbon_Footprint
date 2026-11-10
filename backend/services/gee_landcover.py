"""Satellite-measured area: ESA WorldCover tree cover + Hansen forest loss."""
import ee

from services._gee_init import init_gee

WORLDCOVER_ID = "ESA/WorldCover/v200"  # 10 m, 2021; class 10 = tree cover
HANSEN_ID = "UMD/hansen/global_forest_change_2023_v1_11"  # 30 m, loss years 2001-2023
TREE_CLASS = 10


def measure_land_cover(aoi: ee.Geometry, start_year: int) -> dict:
    """Return tree_cover_ha, aoi_ha, forest_loss_ha (since start_year)."""
    init_gee()
    try:
        land_cover = ee.ImageCollection(WORLDCOVER_ID).first().select("Map")
        tree_cover_m2 = (
            ee.Image.pixelArea()
            .updateMask(land_cover.eq(TREE_CLASS))
            .reduceRegion(
                ee.Reducer.sum(),
                aoi,
                10,
                maxPixels=1e10,
                bestEffort=True,
            )
            .get("area")
        )
        loss_year = ee.Image(HANSEN_ID).select("lossyear")
        loss_m2 = (
            ee.Image.pixelArea()
            .updateMask(loss_year.gte(max(start_year - 2000, 1)))
            .reduceRegion(
                ee.Reducer.sum(),
                aoi,
                30,
                maxPixels=1e10,
                bestEffort=True,
            )
            .get("area")
        )
        values = ee.Dictionary(
            {"tree_cover_m2": tree_cover_m2, "aoi_m2": aoi.area(1), "loss_m2": loss_m2}
        ).getInfo()

        def hectares(key: str) -> float | None:
            value = values.get(key)
            return round(value / 10_000, 1) if value is not None else None

        return {
            "tree_cover_ha": hectares("tree_cover_m2"),
            "aoi_ha": hectares("aoi_m2"),
            "forest_loss_ha": hectares("loss_m2"),
            "source": "ESA WorldCover 2021 + Hansen GFC v1.11",
        }
    except Exception as exc:
        return {
            "tree_cover_ha": None,
            "aoi_ha": None,
            "forest_loss_ha": None,
            "error": str(exc),
        }
