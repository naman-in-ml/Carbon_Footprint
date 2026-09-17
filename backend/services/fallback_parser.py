"""Deterministic claim extraction used when the Nugen API is unavailable.

This parses the same fields the Nugen prompt extracts, so the pipeline works
offline / during a demo without an API key. It is a thin regex/line scan over
the PDD text and only handles the fields the scoring needs.
"""
import re
from typing import Optional


def _find_int(text: str, *patterns: str) -> Optional[int]:
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            try:
                return int(float(m.group(1)))
            except (ValueError, TypeError):
                return None
    return None


def _find_float(text: str, *patterns: str) -> Optional[float]:
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except (ValueError, TypeError):
                return None
    return None


def extract_claims_fallback(text: str, project_id: int) -> dict:
    uncertainties = {}

    claimed_hectares = _find_float(text, r"(\d[\d,.]+)\s*(?:hectares|ha)\b")
    start_year = _find_int(text, r"\b(?:start|planting)\s*(?:years?|start):?\s*(\d{4})", r"(\d{4})\s*[–-]\s*\d{4}")
    claimed_tco2 = _find_float(text, r"(\d[\d,.]+)\s*(?:t|metric)?\s*tCO2\b", r"(\d[\d,.]+)\s*(?:t|metric)?\s*t CO2\b")

    if claimed_hectares is None:
        uncertainties["claimed_hectares"] = "No explicit hectare figure found"
    if start_year is None:
        uncertainties["start_year"] = "No planting start year found"
    if claimed_tco2 is None:
        uncertainties["claimed_tco2"] = "No claimed tCO2 figure found"

    species_m = re.search(r"species[n]?:\s*(.+)", text, re.IGNORECASE)
    species = species_m.group(1).strip() if species_m else None

    baseline_m = re.search(r"(?:baseline|methodology)[^\n:]*[:\s]+([A-Z]{2,}\d{4}[^\n,]*)", text, re.IGNORECASE)
    baseline = baseline_m.group(1).strip() if baseline_m else None

    period_m = re.search(r"monitoring period[:\s]+(\d{4}\s*[–-]\s*\d{4})", text, re.IGNORECASE)
    monitoring_period = period_m.group(1) if period_m else None

    confidence = 0.85
    if not uncertainties:
        confidence = 0.95
    elif len(uncertainties) >= 3:
        confidence = 0.55

    return {
        "project_id_in_doc": None,
        "coordinates_raw": _extract_locations(text) or None,
        "claimed_hectares": claimed_hectares,
        "start_year": start_year,
        "species": species,
        "baseline_method": baseline,
        "claimed_tco2": claimed_tco2,
        "claimed_tco2_per_ha": (
            round(claimed_tco2 / claimed_hectares, 1)
            if claimed_tco2 and claimed_hectares
            else None
        ),
        "monitoring_period": monitoring_period,
        "extraction_confidence": confidence,
        "uncertainty_flags": uncertainties,
        "_source": "fallback_parser",
    }


def _extract_locations(text: str) -> Optional[str]:
    """Grab the most locator-like line: mentions of coordinates or district."""
    for line in text.splitlines():
        if re.search(r"\d{1,3}\.\d+\s*[°NSEW]|district|village|gis|coordinates", line, re.IGNORECASE):
            return line.strip()
    return None