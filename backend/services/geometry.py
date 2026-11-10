"""Pure-Python geometry helpers (no Earth Engine) so they can be unit-tested."""
import json
import math

MIN_RADIUS_M = 250
MAX_RADIUS_M = 5000
DEFAULT_RADIUS_M = 1000


def buffer_radius_m(claimed_hectares: float | None) -> int:
    """Radius of a circle whose area equals the claimed hectares, clamped.

    Used when no project boundary is available: analyse a circle the size of
    the claim instead of a fixed 5 km disc (~7,850 ha) that drowns out small projects.
    """
    if claimed_hectares is None or claimed_hectares <= 0:
        return DEFAULT_RADIUS_M
    radius = round(math.sqrt(claimed_hectares * 10_000 / math.pi))
    return min(max(radius, MIN_RADIUS_M), MAX_RADIUS_M)


def _collect_polygons(value: dict) -> list[list]:
    value_type = value.get("type")
    if value_type == "FeatureCollection":
        polygons = []
        for feature in value.get("features", []):
            polygons.extend(_collect_polygons(feature))
        return polygons
    if value_type == "Feature":
        geometry = value.get("geometry")
        return _collect_polygons(geometry) if isinstance(geometry, dict) else []
    if value_type == "Polygon":
        return [value.get("coordinates", [])]
    if value_type == "MultiPolygon":
        return list(value.get("coordinates", []))
    return []


def _validate_coordinates(polygons: list[list]) -> None:
    for polygon in polygons:
        for ring in polygon:
            for coordinate in ring:
                if len(coordinate) < 2 or abs(coordinate[0]) > 180 or abs(coordinate[1]) > 90:
                    raise ValueError("Coordinates out of range")


def parse_geojson_geometry(text: str) -> dict:
    """Parse uploaded GeoJSON into a single Polygon/MultiPolygon geometry dict."""
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid GeoJSON: {exc}") from exc
    polygons = _collect_polygons(value)
    if not polygons:
        raise ValueError("No polygon found in GeoJSON")
    _validate_coordinates(polygons)
    if len(polygons) == 1:
        return {"type": "Polygon", "coordinates": polygons[0]}
    return {"type": "MultiPolygon", "coordinates": polygons}


def _polygons(geometry: dict) -> list[list]:
    if geometry.get("type") == "Polygon":
        return [geometry["coordinates"]]
    if geometry.get("type") == "MultiPolygon":
        return list(geometry["coordinates"])
    return []


def geometry_area_ha(geometry: dict) -> float:
    """Approximate area in hectares (equirectangular projection + shoelace).

    Accurate to ~1% for project-sized polygons; good enough for a screening check.
    """
    total = 0.0
    for polygon in _polygons(geometry):
        ring = polygon[0]
        if len(ring) < 3:
            continue
        lat0 = sum(point[1] for point in ring) / len(ring)
        projected = [
            (
                point[0] * 111_320 * math.cos(math.radians(lat0)),
                point[1] * 110_540,
            )
            for point in ring
        ]
        shoelace = sum(
            x1 * y2 - x2 * y1
            for (x1, y1), (x2, y2) in zip(projected, projected[1:] + projected[:1])
        )
        total += abs(shoelace) / 2
    return round(total / 10_000, 2)


def geometry_centroid(geometry: dict) -> tuple[float, float]:
    """(lat, lon) = plain average of all outer-ring vertices (screening only)."""
    vertices = []
    for polygon in _polygons(geometry):
        ring = polygon[0]
        vertices.extend(ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else ring)
    if not vertices:
        raise ValueError("No polygon vertices")
    return (
        sum(point[1] for point in vertices) / len(vertices),
        sum(point[0] for point in vertices) / len(vertices),
    )
