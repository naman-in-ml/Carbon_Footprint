"""Nugen interaction: MRV-domain claim extraction + embeddings."""
import json

import httpx

from core.config import settings

EXTRACTION_SYSTEM = """
You are a domain expert in carbon-market MRV (Measurement, Reporting,
Verification).
You are extracting structured data from Project Design Documents (PDDs)
and monitoring reports submitted under Verra VCS or Gold Standard frameworks.
Key terms you will encounter:
- Additionality: proof the project wouldn't have happened without carbon finance
- Permanence: assurance the forest won't be destroyed in future
- Baseline: "what would have happened anyway" scenario
- Buffer pool: reserve credits that insure against reversal losses
- ARR: Afforestation, Reforestation, Revegetation — the project type we focus on
Return ONLY valid JSON. No markdown, no preamble, no explanation text.
"""

EXTRACTION_PROMPT_TEMPLATE = """
Extract the following claims from this PDD/monitoring report excerpt. Be precise.
If a field cannot be found or is ambiguous, set its value to null and add an entry
to the uncertainty_flags object explaining why.
Required schema:
{{
    "project_id_in_doc": "registry project ID if visible",
    "coordinates_raw": "exact text describing location — village, district,
        GPS, polygon WKT, whatever is in the doc",
    "claimed_hectares": number or null,
    "start_year": integer or null,
    "species": "species listed, comma-separated, or null",
    "baseline_method": "methodology code e.g. VM0048, or description",
    "claimed_tco2": number or null,
    "claimed_tco2_per_ha": number or null,
    "monitoring_period": "e.g. 2021–2030",
    "extraction_confidence": float 0.0–1.0,
    "uncertainty_flags": {{"field_name": "reason this field is uncertain"}}
}}
Document excerpt:
\"\"\"
{text}
\"\"\"
"""


def _resolve_model() -> str:
    """Choose the extraction model.

    NUGEN_USE_ALIGNED=false forces the generic model even if an aligned id is
    configured (fallback when the aligned model isn't ready in time).
    """
    if settings.nugen_use_aligned and settings.nugen_aligned_model_id:
        return settings.nugen_aligned_model_id
    return "nugen-flash-instruct"


async def extract_claims(text: str, project_id: int) -> dict:
    model = _resolve_model()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": EXTRACTION_SYSTEM},
            {"role": "user", "content": EXTRACTION_PROMPT_TEMPLATE.format(text=text[:8000])},
        ],
        "max_tokens": 1500,
        "temperature": 0.1,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.nugen_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.nugen_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        raw_text = data["choices"][0]["message"]["content"]
        clean = raw_text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)


async def embed_text(text: str) -> list[float]:
    payload = {
        "model": settings.nugen_embed_model,
        "input": text,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.nugen_base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {settings.nugen_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]