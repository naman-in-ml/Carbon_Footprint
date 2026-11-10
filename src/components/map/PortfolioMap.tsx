"use client";

import "leaflet/dist/leaflet.css";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { CircleMarker, MapContainer, TileLayer, Tooltip, useMap } from "react-leaflet";
import { parsePointWkt } from "@/lib/geo";
import { AFTER_YEAR, imageryAttribution, imageryUrl } from "@/lib/imagery";
import { RISK } from "@/lib/risk";
import type { ScoreListItem } from "@/types";

function FitPoints({ points }: { points: [number, number][] }) {
  const map = useMap();
  useEffect(() => {
    if (points.length >= 2) map.fitBounds(points, { padding: [40, 40] });
  }, [map, points]);
  return null;
}

export function PortfolioMap({ items }: { items: ScoreListItem[] }) {
  const router = useRouter();
  const plotted = items.flatMap((item) => {
    const point = parsePointWkt(item.geometry_wkt);
    return point && item.risk_flag ? [{ item, point }] : [];
  });
  const points: [number, number][] = plotted.map(({ point }) => [point.lat, point.lon]);

  return (
    <MapContainer center={[22.5, 79]} zoom={5} scrollWheelZoom={false} className="h-full w-full">
      <TileLayer
        url={imageryUrl(AFTER_YEAR)}
        attribution={imageryAttribution(AFTER_YEAR)}
        maxNativeZoom={16}
        maxZoom={17}
      />
      {plotted.map(({ item, point }) => {
        const color = RISK[item.risk_flag!].hex;
        return (
          <CircleMarker
            key={item.project_id}
            center={[point.lat, point.lon]}
            radius={9}
            pathOptions={{ color, fillColor: color, fillOpacity: 0.85, weight: 2 }}
            eventHandlers={{ click: () => router.push(`/dashboard/${item.project_id}`) }}
          >
            <Tooltip>
              {item.name} · {item.composite_score?.toFixed(0) ?? "—"}
            </Tooltip>
          </CircleMarker>
        );
      })}
      <FitPoints points={points} />
    </MapContainer>
  );
}
