const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${path}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export async function apiPatch<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PATCH",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${path}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export { API_BASE };

export type Farm = {
  id: string;
  name: string;
  county: string;
  lat: number;
  lon: number;
  nearest_station_id: string;
  cultivars: string[];
  chill_requirement_hours: number;
  production_system: string;
  phenology_stage: string;
  system_rate_in_per_hr: number;
  cold_spot_bias_f: number;
  irrigation_freeze_protection: boolean;
  acres: number;
};

export type Tonight = {
  farm_id: string;
  status: "LOW" | "WATCH" | "PROTECT" | "BEYOND_SYSTEM";
  headline: string;
  weather_fact: string;
  crop_meaning: string;
  suggested_action: string;
  forecast_tmin_f: number | null;
  dewpoint_f: number | null;
  wind_mph: number | null;
  coldest_hour_local: string | null;
  start_threshold_f: number | null;
  confidence: string;
  sources: string[];
  checklist: string[];
  generated_at: string;
};

export type DayOutlook = {
  date: string;
  tmin_f: number | null;
  tmax_f: number | null;
  precip_in: number | null;
  freeze_risk: string;
  disease_wetness_risk: string;
  harvest_rain_risk: string;
  notes?: string | null;
};

export type SevenDay = {
  farm_id: string;
  days: DayOutlook[];
  sources: string[];
  generated_at: string;
};

export type SeasonalCard = {
  period_label: string;
  valid_start: string;
  valid_end: string;
  tmean_anomaly_f: number | null;
  p_freeze_window: number | null;
  expected_freeze_nights: number | null;
  chill_hours_p50: number | null;
  p_chill_shortfall: number | null;
  confidence: string;
  narrative: string;
  method: string;
};

export type Season = {
  farm_id: string;
  chill_to_date_hours: number;
  chill_requirement_hours: number;
  chill_status: string;
  cards: SeasonalCard[];
  disclaimer: string;
  generated_at: string;
  sources: string[];
};
