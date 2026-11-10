import pytest

from services.geometry import (
    buffer_radius_m,
    geometry_area_ha,
    geometry_centroid,
    parse_geojson_geometry,
)

SQUARE = {"type": "Polygon", "coordinates": [[[0, 0], [0.01, 0], [0.01, 0.01], [0, 0.01], [0, 0]]]}


@pytest.mark.parametrize(("hectares", "radius"), [(None, 1000), (0, 1000), (-5, 1000), (100, 564), (1, 250), (1_000_000, 5000)])
def test_buffer_radius(hectares, radius):
    assert buffer_radius_m(hectares) == radius


def test_geometry_area():
    assert geometry_area_ha(SQUARE) == pytest.approx(123.05, rel=0.01)


def test_geometry_centroid():
    assert geometry_centroid(SQUARE) == pytest.approx((0.005, 0.005))


def test_parse_feature_collection_ignores_points():
    value = '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,0]]]}},{"type":"Feature","geometry":{"type":"Point","coordinates":[1,2]}}]}'
    assert parse_geojson_geometry(value)["type"] == "Polygon"


def test_parse_multiple_polygons():
    value = '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,0]]]}},{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[2,2],[3,2],[3,3],[2,2]]]}}]}'
    result = parse_geojson_geometry(value)
    assert result["type"] == "MultiPolygon"
    assert len(result["coordinates"]) == 2


@pytest.mark.parametrize("value", ['{"type":"Point","coordinates":[1,2]}', "not json", '{"type":"Polygon","coordinates":[[[200,10],[1,0],[1,1],[200,10]]]}'])
def test_parse_invalid(value):
    with pytest.raises(ValueError):
        parse_geojson_geometry(value)
