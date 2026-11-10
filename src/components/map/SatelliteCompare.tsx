"use client";

import "leaflet/dist/leaflet.css";
import type { TileLayer as LeafletTileLayer } from "leaflet";
import { useEffect, useRef, useState, type RefObject } from "react";
import { Circle, GeoJSON, MapContainer, TileLayer, useMap } from "react-leaflet";
import type { GeoJsonObject } from "geojson";
import { boundsAround, radiusFromHectares } from "@/lib/geo";
import { AFTER_YEAR, beforeYear, imageryAttribution, imageryUrl } from "@/lib/imagery";
import type { GeoJSONGeometry } from "@/types";

type Props = {
  lat: number;
  lon: number;
  startYear: number | null;
  areaHa: number | null;
  boundary?: GeoJSONGeometry | null;
};

function SwipeClip({
  left,
  right,
  pct,
}: {
  left: RefObject<LeafletTileLayer | null>;
  right: RefObject<LeafletTileLayer | null>;
  pct: number;
}) {
  const map = useMap();
  useEffect(() => {
    const update = () => {
      const leftContainer = left.current?.getContainer();
      const rightContainer = right.current?.getContainer();
      if (!leftContainer || !rightContainer) return;
      const northWest = map.containerPointToLayerPoint([0, 0]);
      const southEast = map.containerPointToLayerPoint(map.getSize());
      const clipX = northWest.x + map.getSize().x * pct;
      leftContainer.style.clip = `rect(${northWest.y}px, ${clipX}px, ${southEast.y}px, ${northWest.x}px)`;
      rightContainer.style.clip = `rect(${northWest.y}px, ${southEast.x}px, ${southEast.y}px, ${clipX}px)`;
    };
    update();
    map.on("move zoom resize zoomend moveend", update);
    left.current?.on("load", update);
    right.current?.on("load", update);
    return () => {
      map.off("move zoom resize zoomend moveend", update);
    };
  }, [left, map, pct, right]);
  return null;
}

export function SatelliteCompare({ lat, lon, startYear, areaHa, boundary }: Props) {
  const [pct, setPct] = useState(0.5);
  const leftRef = useRef<LeafletTileLayer | null>(null);
  const rightRef = useRef<LeafletTileLayer | null>(null);
  const before = beforeYear(startYear);
  const after = AFTER_YEAR;
  const radius = radiusFromHectares(areaHa);
  return (
    <div className="space-y-3">
      <div className="relative h-[440px] overflow-hidden rounded-xl border border-line">
        <MapContainer
          bounds={boundsAround(lat, lon, radius)}
          scrollWheelZoom={false}
          className="h-full w-full"
        >
          <TileLayer
            ref={leftRef}
            url={imageryUrl(before)}
            attribution={imageryAttribution(before)}
            maxNativeZoom={16}
            maxZoom={17}
          />
          <TileLayer
            ref={rightRef}
            url={imageryUrl(after)}
            attribution={imageryAttribution(after)}
            maxNativeZoom={16}
            maxZoom={17}
          />
          {boundary ? (
            <GeoJSON
              data={boundary as GeoJsonObject}
              style={{ color: "#ffffff", weight: 2, dashArray: "6 4", fill: false }}
            />
          ) : (
            <Circle
              center={[lat, lon]}
              radius={radius}
              pathOptions={{ color: "#ffffff", weight: 2, dashArray: "6 4", fill: false }}
            />
          )}
          <SwipeClip left={leftRef} right={rightRef} pct={pct} />
        </MapContainer>
        <div
          className="pointer-events-none absolute inset-y-0 z-[500] w-0.5 bg-white/90 shadow"
          style={{ left: `${pct * 100}%` }}
        />
        <span className="pointer-events-none absolute left-3 top-3 z-[500] rounded-md border border-line bg-white/90 px-2 py-1 font-mono text-xs text-ink shadow-sm">
          {before} · before
        </span>
        <span className="pointer-events-none absolute right-3 top-3 z-[500] rounded-md border border-line bg-white/90 px-2 py-1 font-mono text-xs text-ink shadow-sm">
          {after} · now
        </span>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        value={Math.round(pct * 100)}
        onChange={(event) => setPct(Number(event.target.value) / 100)}
        aria-label="Compare before and after imagery"
        className="w-full accent-emerald-400"
      />
      <p className="text-xs text-muted">
        Dashed outline = analysis area (
        {boundary ? "uploaded boundary" : "circle sized to the claimed hectares"}). Drag the slider
        to compare annual cloud-free Sentinel-2 mosaics.
      </p>
    </div>
  );
}
