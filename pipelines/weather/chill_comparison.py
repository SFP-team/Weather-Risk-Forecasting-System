"""Compare chill definitions on the stored hourly cells: current rule vs AgroClimate band vs Dynamic Model.

Exploratory evidence for the risk-factor review; not wired into the production analysis.
Dynamic Model constants and recursion follow chillR / ChillModels (Fishman, Erez & Couvillon 1987).
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from discover import ROOT, write_json

E0, E1, A0, A1, SLP, TETMLT = 4153.5, 12888.8, 139500.0, 2.567e18, 1.6, 277.0


def chill_portions(temp_c):
    tk = np.asarray(temp_c, dtype=float) + 273.0
    ftmprt = SLP * TETMLT * (tk - TETMLT) / tk
    sr = np.exp(ftmprt)
    xi = sr / (1 + sr)
    xs = A0 / A1 * np.exp((E1 - E0) / tk)
    ak1 = A1 * np.exp(-E1 / tk)
    inter = np.zeros(len(tk))
    for i in range(1, len(tk)):
        prev = inter[i - 1]
        s = prev if prev < 1 else prev - prev * xi[i - 1]
        inter[i] = xs[i] - (xs[i] - s) * np.exp(-ak1[i])
    delta = np.where(inter >= 1, inter * xi, 0.0)
    return np.cumsum(delta)


def winter(series, year, south):
    if south:
        a, b = pd.Timestamp(f'{year}-04-01'), pd.Timestamp(f'{year}-09-01')
        neg = (pd.Timestamp(f'{year}-05-15'), pd.Timestamp(f'{year}-08-15'))
    else:
        a, b = pd.Timestamp(f'{year-1}-10-01'), pd.Timestamp(f'{year}-03-01')
        neg = (pd.Timestamp(f'{year-1}-11-15'), pd.Timestamp(f'{year}-02-15'))
    t = series[a:b - pd.Timedelta(hours=1)]
    if len(t) != int((b - a) / pd.Timedelta(hours=1)) or t.isna().any():
        return None
    cur_a, cur_b = (pd.Timestamp(f'{year}-04-01'), pd.Timestamp(f'{year}-10-01')) if south else (pd.Timestamp(f'{year-1}-11-01'), pd.Timestamp(f'{year}-05-01'))
    cur = series[cur_a:cur_b - pd.Timedelta(hours=1)]
    v = t.to_numpy()
    cp = chill_portions(v)
    band = np.cumsum((v >= 0) & (v <= 7.2))
    first = lambda arr, k: str(t.index[int(np.argmax(arr >= k))].date()) if (arr >= k).any() else None
    return {
        'current_rule_hours_lt_7_2_nov_may': int((cur < 7.2).sum()),
        'hours_lt_7_2_oct_feb': int((v < 7.2).sum()),
        'hours_0_to_7_2_oct_feb': int(band[-1]),
        'hours_below_0': int((v < 0).sum()),
        'chill_portions_oct_feb': round(float(cp[-1]), 1),
        'negation_hours_gt_21_1_midnov_midfeb': int((series[neg[0]:neg[1]] > 21.1).sum()),
        'date_50h_band': first(band, 50), 'date_200h_band': first(band, 200), 'date_300h_band': first(band, 300),
        'date_14cp': first(cp, 14), 'date_21cp': first(cp, 21), 'date_28cp': first(cp, 28),
    }


def run(root=ROOT):
    index = json.loads((root / 'config/hourly_index.json').read_text())
    out = {}
    for key, cell in index['cells'].items():
        series = pd.read_parquet(root / cell['path']).set_index('time').tmean_c
        south = cell['source_lat'] < 0
        rows = {y: winter(series, y, south) for y in range(2011, 2026)}
        valid = [r for r in rows.values() if r]
        mean = lambda k: round(float(np.mean([r[k] for r in valid])), 1)
        p10 = lambda k: round(float(np.percentile([r[k] for r in valid], 10)), 1)
        out[cell['site']] = {
            'cell': key, 'source_lat': cell['source_lat'], 'source_lon': cell['source_lon'], 'valid_winters': len(valid),
            'mean': {k: mean(k) for k in ('current_rule_hours_lt_7_2_nov_may', 'hours_lt_7_2_oct_feb', 'hours_0_to_7_2_oct_feb',
                                          'hours_below_0', 'chill_portions_oct_feb', 'negation_hours_gt_21_1_midnov_midfeb')},
            'safe_winter_chill_p10': {'hours_0_to_7_2': p10('hours_0_to_7_2_oct_feb'), 'chill_portions': p10('chill_portions_oct_feb')},
            'ch_per_cp': round(mean('hours_0_to_7_2_oct_feb') / mean('chill_portions_oct_feb'), 1) if mean('chill_portions_oct_feb') else None,
            'winters': rows,
        }
    write_json(root / 'reports/chill_comparison.json', {'method': 'chill-comparison-v1', 'sites': out})
    for name, s in sorted(out.items(), key=lambda kv: -kv[1]['source_lat']):
        m = s['mean']
        print(f"{name:18s} lat {s['source_lat']:5.1f}  current {m['current_rule_hours_lt_7_2_nov_may']:6.0f}  <7.2 {m['hours_lt_7_2_oct_feb']:6.0f}  0-7.2 {m['hours_0_to_7_2_oct_feb']:6.0f}  <0 {m['hours_below_0']:4.0f}  CP {m['chill_portions_oct_feb']:5.1f}  CH/CP {s['ch_per_cp']}  neg>21 {m['negation_hours_gt_21_1_midnov_midfeb']:5.0f}  p10 CH {s['safe_winter_chill_p10']['hours_0_to_7_2']:5.0f}")


if __name__ == '__main__':
    run()
