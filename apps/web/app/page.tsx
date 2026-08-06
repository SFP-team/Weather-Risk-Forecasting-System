"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { FarmPicker } from "@/components/FarmPicker";
import { apiGet, type Farm, type Tonight } from "@/lib/api";

export default function TonightPage() {
  const params = useSearchParams();
  const [farms, setFarms] = useState<Farm[]>([]);
  const [tonight, setTonight] = useState<Tonight | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const farmId = params.get("farm") || farms[0]?.id || "";

  useEffect(() => {
    apiGet<Farm[]>("/farms")
      .then(setFarms)
      .catch((e) => setError(String(e.message || e)));
  }, []);

  useEffect(() => {
    if (!farmId) return;
    setLoading(true);
    setError(null);
    apiGet<Tonight>(`/farms/${farmId}/tonight`)
      .then(setTonight)
      .catch((e) => setError(String(e.message || e)))
      .finally(() => setLoading(false));
  }, [farmId]);

  if (error && !farms.length) {
    return (
      <div className="error">
        <strong>Cannot reach API.</strong>
        <p className="muted">Start the backend: <code>python -m uvicorn app.main:app --app-dir services/api --port 8000</code></p>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <>
      {farms.length > 0 && farmId && <FarmPicker farms={farms} selectedId={farmId} />}

      {loading && <div className="loading">Loading tonight’s decision…</div>}
      {error && <div className="error">{error}</div>}

      {tonight && !loading && (
        <>
          <section className={`status-banner ${tonight.status}`}>
            <div className={`pill ${tonight.status}`}>{tonight.status.replace("_", " ")}</div>
            <h2>{tonight.headline}</h2>
            <p className="muted" style={{ margin: 0 }}>
              Confidence: {tonight.confidence} · Updated{" "}
              {new Date(tonight.generated_at).toLocaleString()}
            </p>
          </section>

          <div className="grid three">
            <div className="card">
              <div className="muted">Farm low (°F)</div>
              <div className="metric">
                {tonight.forecast_tmin_f ?? "—"}
                <small> °F</small>
              </div>
            </div>
            <div className="card">
              <div className="muted">Dew point</div>
              <div className="metric">
                {tonight.dewpoint_f ?? "—"}
                <small> °F</small>
              </div>
            </div>
            <div className="card">
              <div className="muted">Wind</div>
              <div className="metric">
                {tonight.wind_mph ?? "—"}
                <small> mph</small>
              </div>
            </div>
          </div>

          <div className="grid two">
            <div className="card">
              <h3 style={{ marginTop: 0 }}>What the weather is doing</h3>
              <p className="muted">{tonight.weather_fact}</p>
              <h3>What it means for your crop</h3>
              <p className="muted">{tonight.crop_meaning}</p>
              <h3>Suggested action</h3>
              <p>{tonight.suggested_action}</p>
              {tonight.start_threshold_f != null && (
                <p className="muted">
                  Start threshold guidance: <strong>{tonight.start_threshold_f}°F</strong> open-sky
                  {tonight.coldest_hour_local
                    ? ` · Coldest hour ~ ${tonight.coldest_hour_local}`
                    : ""}
                </p>
              )}
            </div>
            <div className="card">
              <h3 style={{ marginTop: 0 }}>Night checklist</h3>
              <ul className="checklist">
                {tonight.checklist.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
              <p className="muted" style={{ marginTop: "1rem" }}>
                Sources: {tonight.sources.join(" · ")}
              </p>
            </div>
          </div>
        </>
      )}
    </>
  );
}
