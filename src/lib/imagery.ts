export const IMAGERY_YEARS = [2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025] as const;

export function imageryUrl(year: number): string {
  return year === 2016
    ? "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{z}/{y}/{x}.jpg"
    : `https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-${year}_3857/default/g/{z}/{y}/{x}.jpg`;
}

export function imageryAttribution(year: number): string {
  return `Sentinel-2 cloudless by <a href="https://s2maps.eu">EOX IT Services GmbH</a> (contains modified Copernicus Sentinel data ${year})`;
}

/** Latest available year strictly before the project start (fallback: earliest). */
export function beforeYear(startYear: number | null | undefined): number {
  const target = (startYear ?? 2020) - 1;
  const candidates = IMAGERY_YEARS.filter((year) => year <= target);
  return candidates.length ? candidates[candidates.length - 1] : IMAGERY_YEARS[0];
}

export const AFTER_YEAR = IMAGERY_YEARS[IMAGERY_YEARS.length - 1];
