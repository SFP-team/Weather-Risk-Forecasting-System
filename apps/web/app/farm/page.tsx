"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { FarmPicker } from "@/components/FarmPicker";
import { apiGet, apiPatch, type Farm } from "@/lib/api";

const STAGES = [
  "DORMANT",
  "SWELL",
  "PINK",
  "OPEN_BLOOM",
  "PETAL_FALL",
  "GREEN_FRUIT",
  "HARVEST",
];

export default function FarmPage() {
  const params = useSearchParams();
  const [farms, setFarms] = useState<Farm[]>([]);
  const [farm, setFarm] = useState<Farm | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const farmId = params.get("farm") || farms[0]?.id || "";

  useEffect(() => {
    apiGet<Farm[]>("/farms").then(setFarms).catch((e) => setError(String(e.message || e)));
  }, []);

  useEffect(() => {
    if (!farmId) return;
    apiGet<Farm>(`/farms/${farmId}`)
      .then(setFarm)
      .catch((e) => setError(String(e.message || e)));
  }, [farmId]);

  async function save() {
    if (!farm) return;
    setSaving(true);
    setMsg(null);
    try {
      const updated = await apiPatch<Farm>(`/farms/${farm.id}`, {
        phenology_stage: farm.phenology_stage,
        cold_spot_bias_f: farm.cold_spot_bias_f,
        chill_requirement_hours: farm.chill_requirement_hours,
      });
      setFarm(updated);
      setFarms((prev) => prev.map((f) => (f.id === updated.id ? updated : f)));
      setMsg("Saved. Tonight decisions will use the new stage and cold-spot bias.");
    } catch (e: unknown) {
      setError(String(e instanceof Error ? e.message : e));
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      {farms.length > 0 && farmId && <FarmPicker farms={farms} selectedId={farmId} />}
      {error && <div className="error">{error}</div>}
      {farm && (
        <div className="card">
          <h2 style={{ marginTop: 0 }}>{farm.name}</h2>
          <p className="muted">
            {farm.county} County · {farm.acres} acres · nearest station{" "}
            <strong>{farm.nearest_station_id}</strong>
          </p>
          <div className="grid two">
            <div>
              <div className="muted">Cultivars</div>
              <p>{farm.cultivars.join(", ")}</p>
            </div>
            <div>
              <div className="muted">Production system</div>
              <p>{farm.production_system}</p>
            </div>
            <div>
              <label className="muted" htmlFor="stage">
                Phenology stage
              </label>
              <div>
                <select
                  id="stage"
                  value={farm.phenology_stage}
                  onChange={(e) => setFarm({ ...farm, phenology_stage: e.target.value })}
                >
                  {STAGES.map((s) => (
                    <option key={s} value={s}>
                      {s.replaceAll("_", " ")}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="muted" htmlFor="bias">
                Cold-spot bias (°F, negative = colder than FAWN)
              </label>
              <div>
                <input
                  id="bias"
                  type="number"
                  step="0.5"
                  value={farm.cold_spot_bias_f}
                  onChange={(e) =>
                    setFarm({ ...farm, cold_spot_bias_f: parseFloat(e.target.value) })
                  }
                />
              </div>
            </div>
            <div>
              <label className="muted" htmlFor="chill">
                Chill requirement (hours)
              </label>
              <div>
                <input
                  id="chill"
                  type="number"
                  value={farm.chill_requirement_hours}
                  onChange={(e) =>
                    setFarm({
                      ...farm,
                      chill_requirement_hours: parseInt(e.target.value || "0", 10),
                    })
                  }
                />
              </div>
            </div>
            <div>
              <div className="muted">Irrigation system rate</div>
              <p>{farm.system_rate_in_per_hr} in/hr</p>
            </div>
          </div>
          <button className="btn primary" onClick={save} disabled={saving}>
            {saving ? "Saving…" : "Save farm settings"}
          </button>
          {msg && <p className="muted">{msg}</p>}
        </div>
      )}
    </>
  );
}
