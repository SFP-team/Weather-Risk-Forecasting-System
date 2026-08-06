"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { FarmPicker } from "@/components/FarmPicker";
import { apiGet, type Farm, type Season } from "@/lib/api";

export default function SeasonPage() {
  const params = useSearchParams();
  const [farms, setFarms] = useState<Farm[]>([]);
  const [data, setData] = useState<Season | null>(null);
  const [error, setError] = useState<string | null>(null);
  const farmId = params.get("farm") || farms[0]?.id || "";

  useEffect(() => {
    apiGet<Farm[]>("/farms").then(setFarms).catch((e) => setError(String(e.message || e)));
  }, []);

  useEffect(() => {
    if (!farmId) return;
    apiGet<Season>(`/farms/${farmId}/season`)
      .then(setData)
      .catch((e) => setError(String(e.message || e)));
  }, [farmId]);

  const pct = data
    ? Math.min(100, (100 * data.chill_to_date_hours) / data.chill_requirement_hours)
    : 0;

  return (
    <>
      {farms.length > 0 && farmId && <FarmPicker farms={farms} selectedId={farmId} />}
      {error && <div className="error">{error}</div>}
      {data && (
        <>
          <div className="card">
            <h2 style={{ marginTop: 0 }}>Chill progress</h2>
            <div className="metric">
              {data.chill_to_date_hours}
              <small> / {data.chill_requirement_hours} hours</small>
            </div>
            <p className="muted">Status: {data.chill_status.replace("_", " ")}</p>
            <div className="progress" aria-label="chill progress">
              <span style={{ width: `${pct}%` }} />
            </div>
          </div>

          <h2>1–3 month risk cards</h2>
          <p className="muted">
            Probabilistic seasonal guidance — not a daily weather calendar. Method skill is
            vs climatology for monthly tilts, freeze odds, and chill ranges.
          </p>
          <div className="grid">
            {data.cards.map((c) => (
              <div className="card" key={c.period_label}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: "0.5rem" }}>
                  <h3 style={{ margin: 0 }}>{c.period_label}</h3>
                  <span className="pill risk-moderate">{c.confidence} confidence</span>
                </div>
                <div className="grid three" style={{ marginTop: "0.75rem" }}>
                  <div>
                    <div className="muted">P(freeze in window)</div>
                    <div className="metric" style={{ fontSize: "1.25rem" }}>
                      {c.p_freeze_window != null ? `${Math.round(c.p_freeze_window * 100)}%` : "—"}
                    </div>
                  </div>
                  <div>
                    <div className="muted">Expected freeze nights</div>
                    <div className="metric" style={{ fontSize: "1.25rem" }}>
                      {c.expected_freeze_nights ?? "—"}
                    </div>
                  </div>
                  <div>
                    <div className="muted">Chill hours (p50)</div>
                    <div className="metric" style={{ fontSize: "1.25rem" }}>
                      {c.chill_hours_p50 ?? "—"}
                    </div>
                  </div>
                </div>
                {c.p_chill_shortfall != null && (
                  <p className="muted">
                    Chill shortfall probability (heuristic):{" "}
                    <strong>{Math.round(c.p_chill_shortfall * 100)}%</strong>
                  </p>
                )}
                <p>{c.narrative}</p>
                <p className="muted" style={{ marginBottom: 0 }}>
                  Method: {c.method}
                </p>
              </div>
            ))}
          </div>
          <p className="muted">{data.disclaimer}</p>
        </>
      )}
    </>
  );
}
