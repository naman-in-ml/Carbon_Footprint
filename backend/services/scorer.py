"""Stage 5: composite credibility score.

Weights:
  Stage 1 (extraction confidence): 15%
  Stage 2 (planting verified):     35%
  Stage 3 (permanence):            35%
  Stage 4 (credit math):           15%
"""
WEIGHTS = {"extraction": 0.15, "planting": 0.35, "permanence": 0.35, "credit": 0.15}

# Enums used across the pipeline — kept in one place.
CREDIT_FLAG_VALUES = {"ok", "under_claimed", "over_claimed", "major_discrepancy", "ok_limitation"}
RISK_FLAG_VALUES = {"low", "medium", "high", "critical"}


def map_credit_flag_to_risk(credit_flag: str | None) -> str:
    """Explicit mapping between the two enums.

    credit_flag describes the *credit math* result (Stage 4), while risk_flag is
    the composite severity band (Stage 5). This function is the single place the
    Stage-4 enum becomes an input band for scoring; it does NOT replace the
    weighted composite — it only converts a single signal.
    """
    if credit_flag == "major_discrepancy":
        return "critical"
    if credit_flag == "over_claimed":
        return "high"
    if credit_flag == "under_claimed":
        return "medium"
    return "low"  # ok / None


def score_extraction(confidence: float, requires_review: bool) -> float:
    base = (confidence or 0.5) * 100
    if requires_review:
        base *= 0.7
    return round(min(base, 100), 1)


def score_planting(planting_verified: str, confidence: float) -> float:
    base = {"yes": 90, "partial": 55, "no": 10, "unknown": 40}.get(planting_verified, 40)
    return round(base * (0.6 + 0.4 * (confidence or 0.5)), 1)


def score_permanence(still_standing: str, fire_events: int, decline_detected: bool) -> float:
    base = {"yes": 95, "partial": 60, "no": 10}.get(still_standing, 50)
    if fire_events and fire_events > 0:
        base = min(base, 50)
    if decline_detected:
        base = min(base, 40)
    return round(base, 1)


def score_credit_math(credit_flag: str | None) -> float:
    return {
        "ok": 95,
        "under_claimed": 80,
        "over_claimed": 45,
        "major_discrepancy": 10,
        None: 50,
    }.get(credit_flag, 50)


def compute_composite(
    extraction_confidence: float,
    requires_review: bool,
    planting_verified: str,
    planting_confidence: float,
    still_standing: str,
    fire_events_detected: int,
    decline_detected: bool,
    credit_flag: str,
) -> dict:
    s_ext = score_extraction(extraction_confidence, requires_review)
    s_plt = score_planting(planting_verified, planting_confidence)
    s_perm = score_permanence(still_standing, fire_events_detected, decline_detected)
    s_cred = score_credit_math(credit_flag)

    composite = (
        s_ext * WEIGHTS["extraction"]
        + s_plt * WEIGHTS["planting"]
        + s_perm * WEIGHTS["permanence"]
        + s_cred * WEIGHTS["credit"]
    )

    if composite >= 75:
        risk_flag = "low"
    elif composite >= 50:
        risk_flag = "medium"
    elif composite >= 30:
        risk_flag = "high"
    else:
        risk_flag = "critical"

    flag_reasons = {}
    if s_plt < 50:
        flag_reasons["planting"] = "Satellite NDVI does not support claimed reforestation"
    if s_perm < 50:
        flag_reasons["permanence"] = "Forest loss or fire events detected post-planting"
    if s_cred < 50:
        flag_reasons["credit_math"] = "Satellite estimate diverges >30% from claimed tCO2"
    if s_ext < 50:
        flag_reasons["extraction"] = "Low-confidence claim extraction — document may be incomplete"

    # Cross-check the composite risk band against the Stage-4 credit signal.
    credit_risk = map_credit_flag_to_risk(credit_flag)
    if credit_risk == "critical" and risk_flag not in ("critical", "high"):
        flag_reasons["credit_math_severity"] = (
            f"Credit discrepancy alone maps to '{credit_risk}'; composite is '{risk_flag}'"
        )

    return {
        "extraction_score": s_ext,
        "planting_score": s_plt,
        "permanence_score": s_perm,
        "credit_math_score": s_cred,
        "composite_score": round(composite, 1),
        "risk_flag": risk_flag,
        "flag_reasons": flag_reasons,
    }