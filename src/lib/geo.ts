/** Parse "POINT(lon lat)" → { lat, lon } or null. Longitude comes first in WKT. */
export function parsePointWkt(wkt: string | null | undefined): { lat: number; lon: number } | null {
  if (!wkt) return null;
  const match = wkt.match(/POINT\s*\(\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*\)/i);
  if (!match) return null;
  return { lon: Number(match[1]), lat: Number(match[2]) };
}

/** Radius (m) of a circle with the given area in hectares. */
export function radiusFromHectares(ha: number | null | undefined, fallback = 1000): number {
  if (!ha || ha <= 0) return fallback;
  return Math.min(Math.max(Math.sqrt((ha * 10_000) / Math.PI), 250), 5000);
}

/** Lat/lon bounds around a point with radius r (m), padded by `pad`. */
export function boundsAround(
  lat: number,
  lon: number,
  radius: number,
  pad = 1.8,
): [[number, number], [number, number]] {
  const dLat = (radius * pad) / 111_320;
  const dLon = (radius * pad) / (111_320 * Math.cos((lat * Math.PI) / 180));
  return [
    [lat - dLat, lon - dLon],
    [lat + dLat, lon + dLon],
  ];
}
