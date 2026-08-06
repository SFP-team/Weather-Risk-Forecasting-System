"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { FarmPicker } from "@/components/FarmPicker";
import { apiGet, type Farm, type SevenDay } from "@/lib/api";

export default function SevenDayPage() {
  const params = useSearchParams();
  const [farms, setFarms] = useState<Farm[]>([]);
  const [data, setData] = useState<SevenDay | null>(null);
  const [error, setError] = useState<string | null>(null);
  const farmId = params.get("farm") || farms[0]?.id || "";

  useEffect(() => {
    apiGet<Farm[]>("/farms").then(setFarms).catch((e) => setError(String(e.message || e)));
  }, []);

  useEffect(() => {
    if (!farmId) return;
    setError(null);
    apiGet<SevenDay>(`/farms/${farmId}/seven-day`)
      .then(setData)
      .catch((e) => setError(String(e.message || e)));
  }, [farmId]);

  return (
    <>
      {farms.length > 0 && farmId && <FarmPicker farms={farms} selectedId={farmId} />}
      {error && <div className="error">{error}</div>}
      {data && (
        <div className="card">
          <h2 style={{ marginTop: 0 }}>7-day operational outlook</h2>
          <p className="muted">
            Freeze, wetness, and harvest-rain risk for planning labor and sprays. Sources:{" "}
            {data.sources.join(" · ")}
          </p>
          {data.days.map((d) => (
            <div className="day-row" key={d.date}>
              <div>
                <strong>
                  {new Date(d.date + "T12:00:00").toLocaleDateString(undefined, {
                    weekday: "short",
                    month: "short",
                    day: "numeric",
                  })}
                </strong>
                <div className="muted">
                  {d.tmin_f ?? "—"}° / {d.tmax_f ?? "—"}°
                  {d.precip_in != null ? ` · ${d.precip_in.toFixed(2)}"` : ""}
                </div>
              </div>
              <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", alignItems: "center" }}>
                <span className={`pill risk-${d.freeze_risk}`}>Freeze {d.freeze_risk}</span>
                <span className={`pill risk-${d.disease_wetness_risk}`}>
                  Wetness {d.disease_wetness_risk}
                </span>
                <span className={`pill risk-${d.harvest_rain_risk}`}>
                  Harvest rain {d.harvest_rain_risk}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
