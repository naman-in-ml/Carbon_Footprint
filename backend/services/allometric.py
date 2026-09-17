"""Stage 4: allometric biomass -> tCO2 estimate + credit reconciliation.

The satellite estimate is an ORDER-OF-MAGNITUDE SCREENING ESTIMATE, not an
audit. We deliberately widen the uncertainty band (+/-50%) and only flag gross
over-crediting (>30% divergence beyond that band).
"""
SPECIES_BIOMASS_THA = {
    "teak": 120,
    "eucalyptus": 80,
    "bamboo": 60,
    "acacia": 100,
    "mixed broadleaf": 90,
    "mixed tropical": 110,
    "default": 90,
}

UNCERTAINTY_PCT = 50  # +/- 50% — honest screening band for allometric proxies

CARBON_FRACTION = 0.475
CO2_TO_C_RATIO = 44 / 12


def ndvi_to_canopy_fraction(ndvi: float) -> float:
    if ndvi is None:
        return 0.0
    if ndvi >= 0.50:
        return 1.00
    if ndvi >= 0.35:
        return 0.60
    if ndvi >= 0.20:
        return 0.30
    return 0.00


def estimate_tco2(verified_hectares: float, ndvi_current: float, species_text: str | None) -> dict:
    species_key = "default"
    if species_text:
        for key in SPECIES_BIOMASS_THA:
            if key.lower() in species_text.lower():
                species_key = key
                break
    biomass_tha = SPECIES_BIOMASS_THA[species_key]

    canopy_fraction = ndvi_to_canopy_fraction(ndvi_current)
    above_ground = (
        verified_hectares * biomass_tha * canopy_fraction * CARBON_FRACTION * CO2_TO_C_RATIO
    )
    total_tco2 = above_ground * 1.25  # +25% below-ground (IPCC root-to-shoot ratio)

    low = total_tco2 * (1 - UNCERTAINTY_PCT / 100)
    high = total_tco2 * (1 + UNCERTAINTY_PCT / 100)

    return {
        "estimated_tco2": round(total_tco2, 1),
        "uncertainty_pct": UNCERTAINTY_PCT,
        "low_estimate": round(low, 1),
        "high_estimate": round(high, 1),
        "species_used": species_key,
        "canopy_fraction": canopy_fraction,
        "method": "IPCC-2006 allometric + NDVI canopy proxy (order-of-magnitude)",
    }


def reconcile_credits(claimed_tco2: float, estimated_tco2: float, uncertainty_pct: float = UNCERTAINTY_PCT) -> dict:
    """Compare claimed vs estimated tCO2. Only flag outside the uncertainty band."""
    delta_pct = (claimed_tco2 - estimated_tco2) / max(claimed_tco2, 1) * 100
    band = uncertainty_pct
    if delta_pct > 1.1 * band:
        flag = "major_discrepancy"
    elif delta_pct > band * 0.6:
        flag = "over_claimed"
    elif delta_pct < -band * 0.6:
        flag = "under_claimed"
    else:
        flag = "ok"
    return {"credit_delta_pct": round(delta_pct, 1), "credit_flag": flag}