# CarbonProof

**Carbon credits, fact-checked from orbit.**

CarbonProof screens reforestation (ARR) carbon-credit projects by comparing what a
project's design document _claims_ against what independent satellite data
_shows_. Each project gets a 0–100 credibility score and a risk flag, so auditors
can review the weakest claims first.

> CarbonProof is a **screening tool**, not a certified MRV methodology. Its
> estimates are order-of-magnitude checks meant to prioritise human review.

## How it works

The pipeline runs in four stages, then combines them into a composite score:

| Stage          | What it does                                                                                                                                                                                              | Data source                                           |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| 1. Extract     | Pulls location, hectares, start year, species and claimed tCO₂ out of a PDD (PDF or pasted text). Falls back to a regex parser if no LLM key is set. Locations without coordinates are geocoded (cached). | Nugen LLM · OpenStreetMap Nominatim                   |
| 2. Planting    | Compares NDVI before and after planting against an offset control region (difference-in-differences).                                                                                                     | Sentinel-2 SR (cloud-masked) via Google Earth Engine  |
| 3. Permanence  | Annual NDVI time series to detect decline, plus fire detections and forest-loss area since project start.                                                                                                 | Sentinel-2 · NASA FIRMS · Hansen Global Forest Change |
| 4. Credit math | Estimates tCO₂ from satellite tree-cover area × species biomass (IPCC 2006 defaults) and compares it with the claimed credits.                                                                            | ESA WorldCover · IPCC defaults                        |

**Composite score** = extraction 15% + planting 35% + permanence 35% + credit math 15%,
with caps for hard red flags (e.g. tree cover far below the claimed area, major
forest loss, no planting detected). Every flag comes with a human-readable reason
that shows up on the dashboard.

The analysis area is the uploaded project boundary if one exists, otherwise a
circle sized to the claimed hectares (250 m–5 km radius).

## Tech stack

- **Frontend:** Next.js 16 (App Router), React 19, Tailwind CSS 4, TanStack Query,
  Recharts, Leaflet (before/after Sentinel-2 imagery swipe map)
- **Backend:** FastAPI, SQLModel + asyncpg, Google Earth Engine Python API
- **Database:** Postgres on Supabase (schema in `supabase/migrations/`)

## Repository layout

```
src/                     Next.js frontend
  app/                   Routes: / (landing), /projects (portfolio), /dashboard/[projectId]
  components/            dashboard/, map/, layout/, ui/
  hooks/useProject.ts    Data fetching; falls back to demo data if the API is unreachable
  lib/demoData.ts        GENERATED demo data (see scripts/gen_demo_data.py)
backend/
  api/index.py           FastAPI app entry point
  routers/               /api/projects, /api/ingest, /api/verify, /api/scores
  pipeline/orchestrator  Runs the extract → verify → score stages
  services/              Earth Engine, scoring, geocoding, LLM extraction
  tests/                 pytest suite (pure logic, no network or Earth Engine needed)
scripts/
  demo_projects.py       The four fictional demo projects
  gen_demo_data.py       Regenerates src/lib/demoData.ts from the real scorer
  seed_projects.py       Loads the demo projects into the database
supabase/migrations/     SQL schema; apply in order
start.sh                 One-command local dev launcher
```

## Quick start (demo mode, no credentials)

The frontend runs on its own using built-in demo data. It's labelled as demo data in the UI.

```bash
npm install
./start.sh          # or: npm run dev
```

Open http://localhost:3000. You'll see four fictional projects covering the main
cases: a healthy restoration, an over-claimed agroforestry project, a
"phantom forest" with no planting, and a project hit by fire and forest loss.

## Full setup (live pipeline)

### 1. Prerequisites

- Node.js 20+ and Python 3.12
- A Supabase (Postgres) project
- A Google Earth Engine service account with Earth Engine API access
- Optional: a Nugen API key (without it, the regex fallback parser is used)

### 2. Environment

```bash
cp .env.example .env
```

| Variable                        | Required | Purpose                                                         |
| ------------------------------- | -------- | --------------------------------------------------------------- |
| `DATABASE_URL`                  | yes      | Supabase Postgres, `postgresql+asyncpg://…` (pooler URL)        |
| `GEE_SERVICE_ACCOUNT`           | yes      | Earth Engine service-account email                              |
| `GEE_KEY_FILE` / `GEE_KEY_JSON` | one of   | Key file path (local) or the full key JSON as one line (hosted) |
| `NUGEN_API_KEY`, `NUGEN_*`      | no       | LLM claim extraction                                            |
| `ALLOWED_ORIGINS`               | no       | CORS origins for the API (default `http://localhost:3000`)      |
| `BACKEND_URL`                   | no       | Frontend only: where to proxy `/api/*` in production            |

Never commit `.env` or `backend/gee-key.json`; both are gitignored.

### 3. Database

Run the migrations in order in the Supabase SQL editor (or `psql`):

```
supabase/migrations/001_initial_schema.sql
supabase/migrations/002_satellite_area.sql
```

The backend does not create tables itself.

### 4. Backend

```bash
cd backend
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
cd ..
python scripts/gee_smoke_test.py         # optional: checks Earth Engine access
backend/.venv/bin/python scripts/seed_projects.py   # optional: load demo projects
```

### 5. Run

```bash
set -a; source .env; set +a   # start.sh checks DATABASE_URL in the shell env
./start.sh
```

This starts FastAPI on `:8000` and Next.js on `:3000`. In development, Next.js
proxies `/api/*` to the backend. API docs: http://localhost:8000/docs.

## Using the API

```bash
# 1. Ingest a PDD (PDF upload, or POST /api/ingest/text with a `text` field)
curl -F verra_id=VCS-1234 -F name="My ARR Project" -F file=@pdd.pdf \
  http://localhost:8000/api/ingest/

# 2. Run satellite verification (calls Earth Engine; can take a minute)
curl -X POST http://localhost:8000/api/verify/1

# 3. Compute the credibility score
curl -X POST http://localhost:8000/api/scores/score/1

# Read results
curl http://localhost:8000/api/scores/      # portfolio list
curl http://localhost:8000/api/scores/1     # full project detail
```

## Development

```bash
cd backend && .venv/bin/python -m pytest -q   # backend tests
npm run lint                                  # ESLint
npm run format:check                          # Prettier (npm run format to fix)
npm run build                                 # production build + type check
```

After changing the scorer or `scripts/demo_projects.py`, regenerate the frontend
demo data. Don't edit `src/lib/demoData.ts` by hand:

```bash
backend/.venv/bin/python scripts/gen_demo_data.py
```

## Deployment

The repo deploys to Vercel as a Next.js app (`vercel.json`). The FastAPI backend
is **not** deployed by that config. Without `BACKEND_URL`, the deployed site runs
in demo mode. To go live, host the backend separately (any ASGI host) and set
`BACKEND_URL` on the Vercel project.

## Known limitations

- **Tree cover is a 2021 snapshot** (ESA WorldCover). Young saplings and projects
  started after 2021 may not show up as tree cover yet, and pre-existing forest
  counts toward the area.
- **The control region is a fixed offset**, not a matched site. Its soil and land
  use may differ from the project's.
- **Fire detections are 1 km resolution.** Very small sites may miss fires, and
  nearby agricultural burning can be picked up.
- **Carbon estimates use generic IPCC biomass defaults** per species group.
  They're good enough to spot large discrepancies, not to issue credits.
- **Boundary upload isn't wired up yet.** The data model supports a GeoJSON
  boundary, but no endpoint sets it, so analysis currently uses the
  claim-sized circle.

## Data & imagery credits

Sentinel-2 cloudless mosaics by [EOX IT Services GmbH](https://s2maps.eu)
(contains modified Copernicus Sentinel data). The 2018+ mosaics are licensed
CC BY-NC-SA 4.0, so commercial use needs a separate licence. Also uses ESA
WorldCover, Hansen/UMD Global Forest Change, NASA FIRMS, and OpenStreetMap
Nominatim.
