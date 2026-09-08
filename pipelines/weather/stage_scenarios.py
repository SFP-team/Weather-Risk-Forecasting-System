"""Offline, uncalibrated Paul-derived stage scenarios; never cultivar predictions."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from discover import write_json
from evidence_report import complete, dry_spell, table
from postprocess import ROOT, LandMask, extract

METRICS = ('flower_freeze_days', 'harvest_rain_mm', 'harvest_heavy_rain_days',
           'production_max_dry_days')
LIMITATIONS = [
    'Exploratory sensitivity only: neither 50 nor 100 hours is a calibrated cultivar requirement.',
    'Paul-derived strict T < 7.2°C includes freezing hours. Six-month windows: Apr–Sep south; Nov–Apr north. UTC throughout, not original LST.',
    'GDD base 7°C, 150 GDD to assumed budbreak, including the chill-fulfilment day. Flowering budbreak +14 to +35 days; harvest flowering start +70 to +110 days. Endpoints inclusive.',
    'Full hourly chill window required. Missing thermal-time days stop calculation; incomplete or suspect rainfall windows are unavailable, never zero-filled.',
    'Freeze means daily minimum ≤ −2.2°C during assumed flowering; heavy rain ≥10 mm/day; dry spell rain <1 mm/day. These are exposures, not yield-loss probabilities.',
    'Gridded data missed observed cold days in the 2020 station pilot. No bias correction, disease model, cultivar ranking or exact reproduction of Paul’s reports.',
    'Years identify actual southern winter or northern winter ending year, not Paul’s southern crop-year label. Paired effects use only years valid in both scenarios for each metric.',
]


def scenario(hourly, daily, start, end, requirement):
    if requirement <= 0: raise ValueError('Positive chill requirement required')
    winter = complete(hourly, start, end, 'h')
    result = {'requirement_hours': requirement, 'status': 'incomplete_chill',
              'metrics': {k: None for k in METRICS}, 'metric_issues': {}}
    if winter is None: return result
    reached = (winter < 7.2).cumsum() >= requirement
    if not reached.any():
        result['status'] = 'chill_not_met'
        return result
    trigger = reached[reached].index[0].floor('D')
    result['chill_date'] = str(trigger.date())
    if daily.index.has_duplicates: raise ValueError('Duplicate daily timestamps')
    total = 0.
    bud = None
    for day in pd.date_range(trigger, pd.Timestamp(start) + pd.Timedelta(days=450)):
        temp = daily.tmean_c.get(day, np.nan)
        if not np.isfinite(temp):
            result['status'] = 'incomplete_gdd'
            return result
        total += max(float(temp) - 7, 0)
        if total >= 150:
            bud = day
            break
    if bud is None:
        result['status'] = 'gdd_not_met_within_horizon'
        return result
    flower = (bud + pd.Timedelta(days=14), bud + pd.Timedelta(days=35))
    harvest = (flower[0] + pd.Timedelta(days=70), flower[0] + pd.Timedelta(days=110))
    result.update(budbreak_date=str(bud.date()),
                  flowering=[str(d.date()) for d in flower],
                  harvest=[str(d.date()) for d in harvest])
    one = pd.Timedelta(days=1)
    cold = complete(daily.tmin_c, flower[0], flower[1]+one, 'D')
    result['metrics']['flower_freeze_days'] = None if cold is None else int((cold <= -2.2).sum())
    rain = daily.precip_mm.copy()
    # Honor explicit upstream flags, including any future flags below 1000 mm.
    if 'precip_suspect_extreme' in daily:
        rain = rain.mask(daily.precip_suspect_extreme.fillna(True).astype(bool))
    rain = rain.mask((rain < 0) | (rain > 1000))
    wet = complete(rain, harvest[0], harvest[1]+one, 'D')
    if wet is not None:
        result['metrics']['harvest_rain_mm'] = float(wet.sum())
        result['metrics']['harvest_heavy_rain_days'] = int((wet >= 10).sum())
    result['metrics']['production_max_dry_days'] = dry_spell(rain, start, harvest[1]+one)
    for key, value in result['metrics'].items():
        if value is None:
            result['metric_issues'][key] = ('missing/nonfinite temperature window' if key == 'flower_freeze_days'
                                          else 'missing/nonfinite/negative/suspect rainfall window')
    result['status'] = 'complete' if not result['metric_issues'] else 'incomplete_metrics'
    return result


def paired(rows):
    output = {}
    for metric in METRICS:
        pairs = [(r['scenarios'][0]['metrics'][metric], r['scenarios'][1]['metrics'][metric]) for r in rows]
        valid = [(a,b) for a,b in pairs if a is not None and b is not None]
        output[metric] = {'paired_years': len(valid),
            'mean_50': float(np.mean([a for a,b in valid])) if valid else None,
            'mean_100': float(np.mean([b for a,b in valid])) if valid else None,
            'mean_difference_100_minus_50': float(np.mean([b-a for a,b in valid])) if valid else None}
    return output


def run(root=ROOT):
    report = {'method': 'exploratory-stage-scenarios-v1', 'limitations': LIMITATIONS,
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'sites': {}}
    land = LandMask(root)
    for site in json.loads((root/'config/sites.json').read_text()):
        if site['name'] not in ('Papanduva','Citra','Waldo'): continue
        daily, provenance = extract(root, site['lat'], site['lon'], land, padding=True)
        if daily is None: raise ValueError('Unsupported site')
        daily = daily.set_index('time')
        source = root/'data/normalized/pilot/pilot'/site['id']/'met_hourly.parquet'
        hourly = pd.read_parquet(source).set_index('time').tmean_c
        rows = []
        for year in range(2011,2026):
            start,end = (f'{year}-04-01',f'{year}-10-01') if site['lat'] < 0 else (f'{year-1}-11-01',f'{year}-05-01')
            rows.append({'winter_year': year, 'start': start, 'end_exclusive': end,
                         'scenarios': [scenario(hourly,daily,start,end,n) for n in (50,100)]})
        report['sites'][site['name']] = {'annual': rows, 'paired': paired(rows),
            'daily_provenance': provenance, 'hourly_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
    out = root/'reports/stage_scenarios'
    out.mkdir(parents=True,exist_ok=True)
    write_json(out/'stage_scenarios.json',report)
    parts = ['<!doctype html><html lang="en"><meta charset="utf-8"><title>Exploratory seasonal exposures</title>',
        '<style>body{font:16px system-ui;max-width:1150px;margin:40px auto;padding:20px;color:#173a3a}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:9px;border-bottom:1px solid #ccd;text-align:left}.scroll{overflow:auto}li{margin:10px 0}h1,h2{color:#176b65}</style>',
        '<h1>How assumed seasonal timing changes exposure</h1><p>Three sites · 2011–2025 winters · existing NASA POWER weather · <strong>not cultivar advice</strong></p>',
        '<h2>Assumptions and limits</h2><ul>'+''.join('<li>'+x+'</li>' for x in LIMITATIONS)+'</ul>',
        '<p>Means below are paired by winter. Differences are 100-hour minus 50-hour scenario; positive does not automatically mean worse. Zero freeze days is not proof of frost safety.</p>']
    for name,data in report['sites'].items():
        parts += ['<h2>'+name+'</h2>',table(['Metric','Paired winters / 15','50 h mean','100 h mean','Difference'],
            [[k,v['paired_years'],v['mean_50'],v['mean_100'],v['mean_difference_100_minus_50']] for k,v in data['paired'].items()])]
        parts += [table(['Winter','Trigger h','Status','Chill date','Assumed flowering','Assumed harvest',*METRICS],
            [[r['winter_year'],s['requirement_hours'],s['status'],s.get('chill_date'),
              ' → '.join(s.get('flowering',[])) or None,' → '.join(s.get('harvest',[])) or None,
              *[s['metrics'][k] for k in METRICS]] for r in data['annual'] for s in r['scenarios']])]
    (out/'stage_scenarios.html').write_text('\n'.join(parts)+'</html>')
    print(json.dumps({name:data['paired'] for name,data in report['sites'].items()}))


if __name__ == '__main__': run()
