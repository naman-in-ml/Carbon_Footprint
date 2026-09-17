"""Geocoding: coordinates straight from the doc, else Nominatim (cached).

Nominatim's public service allows ~1 request/sec and requires a meaningful
User-Agent header. All results are cached in the `geocode_cache` table so the
pipeline never re-hits the rate limit for the same location.
"""
import logging
import re

import httpx
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models.geocode_cache import GeocodeCache

logger = logging.getLogger(__name__)

COORD_RE = re.compile(r"(-?\d{1,3}\.\d+)\s*[°]?\s*([NS])?\s*[\s,]+(-?\d{1,3}\.\d+)\s*[°]?\s*([EW])?\s*")
GEOCODE_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "carbonproof-mvp/0.1 (carbon verification demo)"


def extract_coordinates_from_text(raw: str):
    """Return (lat, lon) with hemisphere handling, or None."""
    if not raw:
        return None
    m = COORD_RE.search(raw)
    if not m:
        return None
    lat, lat_dir, lon, lon_dir = float(m.group(1)), m.group(2), float(m.group(3)), m.group(4)
    # Only apply hemisphere direction when the sign isn't already present.
    if lat_dir == "S" and lat > 0:
        lat = -lat
    if lon_dir == "W" and lon > 0:
        lon = -lon
    if abs(lat) > 90 or abs(lon) > 180:
        return None
    return lat, lon


async def _geocode_nominatim(query: str):
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            GEOCODE_URL,
            params={"q": query, "format": "json", "limit": 1},
            headers={"User-Agent": USER_AGENT},
        )
        resp.raise_for_status()
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    return None


async def geocode_location(db: AsyncSession, location_string: str, country: str = "India"):
    """Geocode with cache. Returns (lat, lon) or None on failure."""
    query = f"{location_string or ''}, {country}".strip(", ")
    # Check cache first.
    cached = (
        await db.execute(select(GeocodeCache).where(GeocodeCache.query == query))
    ).scalars().first()
    if cached:
        return cached.lat, cached.lon
    try:
        coords = await _geocode_nominatim(query)
    except Exception as exc:  # network / rate-limit — treat as cache miss
        logger.warning("Nominatim lookup failed for %r: %s", query, exc)
        coords = None
    if coords:
        db.add(GeocodeCache(query=query, lat=coords[0], lon=coords[1], method="nominatim"))
        await db.commit()
    return coords


async def resolve_geometry(db: AsyncSession, coordinates_raw: str, country: str = "India") -> dict:
    coords = extract_coordinates_from_text(coordinates_raw or "")
    if coords:
        return {"lat": coords[0], "lon": coords[1], "method": "doc"}
    coords = await geocode_location(db, coordinates_raw, country)
    if coords:
        return {"lat": coords[0], "lon": coords[1], "method": "nominatim"}
    return {"lat": None, "lon": None, "method": "failed"}