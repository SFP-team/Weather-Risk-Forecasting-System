"""Literature benchmark: modelled production system and stage months versus published regional practice.

`benchmark_sites.json` holds expectations compiled from published sources before any model comparison.
Agreement is descriptive evidence for model review. It is not validation against field observations:
regional calendars mix cultivars, management and years, while the model is one grid cell and one
parameter set.
"""
import hashlib
import html
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from discover import ROOT, write_json
from evidence_report import table
from location_api import hourly_for
from postprocess import LandMask, extract
from production import METHOD, analyse, month_day, months_between

REGISTRY = Path(__file__).with_name('benchmark_sites.json')
COMPARED = ('stage_risks_v2', 'stage_thermal_v3')
MONTHS = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
# Evergreen < semi-evergreen < deciduous; `mixed` practice (both systems) sits with semi-evergreen.
MODEL_ORDER = {'Evergreen': 0, 'Semi-evergreen': 1, 'Deciduous': 2}
PRACTICE_ORDER = {'evergreen': 0, 'semi_evergreen': 1, 'mixed': 1, 'deciduous': 2}


def month_gap(month, months):
    """Circular distance in months from `month` to the nearest month of `months`; 0 inside."""
    return min(min(abs(month - m), 12 - abs(month - m)) for m in months)


def midpoint_month(first, last):
    a, b = pd.Timestamp(f'2001-{first}'), pd.Timestamp(f'2001-{last}')
    if b < a:
        b += pd.DateOffset(years=1)
    return (a + (b - a) / 2).month


def overlap(model, expected, midpoint=None):
    """Month-set agreement. Recall: share of published months the model covers; precision: share of model months
    published. An empty model window is a miss (recall 0, precision undefined), never skipped."""
    if not expected:
        return None
    shared = len(set(model) & set(expected))
    out = {'model_months': sorted(model), 'empty': not model, 'recall': shared / len(set(expected)),
           'precision': shared / len(set(model)) if model else None,
           'jaccard': shared / len(set(model) | set(expected))}
    if midpoint is not None:
        out.update(midpoint_month=midpoint, midpoint_inside=midpoint in expected,
                   midpoint_gap_months=month_gap(midpoint, expected))
    return out


def system_score(model, practice):
    """1 same class, 0.5 adjacent, 0 opposite. A failed two-thirds vote (Transitional) is never an exact match."""
    if practice not in PRACTICE_ORDER:
        return None
    if model == 'Transitional':
        return 0.5
    if model not in MODEL_ORDER:
        return None
    return {0: 1.0, 1: 0.5}.get(abs(MODEL_ORDER[model] - PRACTICE_ORDER[practice]), 0.0)


def stage_windows(result):
    """Bloom and harvest months from the chill-triggered calendar, or from a primary managed-cycle scan.

    A chill-clock window needs as many winters with a calendar as the profile's risk policy (the v3 applicability
    threshold), for every profile, so legacy and v3 windows are scored on the same evidence."""
    cycle = result.get('managed_cycle')
    if cycle and cycle['role'] == 'primary':
        favourable = cycle['favourable']
        return {'source': 'managed_cycle', 'unconstrained': favourable['unconstrained'],
                'bloom': (favourable['flowering_months'], None), 'harvest': (favourable['harvest_months'], None)}
    cal = result['calendar']
    if ((cycle is None and result['risks']['by_id']['chill_shortfall']['eligibility'] == 'not_applicable')
            or cal['harvest_end']['n'] < result['risks']['policy']['min_valid_years']):
        return {'source': None, 'bloom': ([], None), 'harvest': ([], None)}
    out = {'source': 'chill_clock'}
    for stage, (a, b) in (('bloom', ('flowering_start', 'flowering_end')), ('harvest', ('harvest_start', 'harvest_end'))):
        first, last = cal[a].get('median_date'), cal[b].get('median_date')
        out[stage] = (months_between(first, last), midpoint_month(first, last)) if first and last else ([], None)
    return out


def assess(site, hourly, daily, profile_name):
    """`hourly`: frame of tmean_c and dewpoint_mean_c for the site's source cell."""
    result = analyse(hourly.tmean_c, daily, site['lat'], profile_name, dewpoint=hourly.dewpoint_mean_c, lon=site['lon'])
    classes = result['classification']['multi_feature']
    windows = stage_windows(result)
    budbreak = result['calendar']['budbreak'].get('median_date') if windows['source'] == 'chill_clock' else None
    # Supervisor's R rule, tested here rather than adopted: plant from 105 to 30 days before median budbreak.
    planting = months_between(month_day(budbreak, -105), month_day(budbreak, -30)) if budbreak else []
    return {
        'system': classes['majority'], 'system_share': classes['majority_share'],
        'system_score': system_score(classes['majority'], site['production_system']),
        'year_counts': classes['year_counts'], 'status_counts': result['status_counts'],
        'chill_hours_mean': result['chill_hours'].get('mean'), 'chill_portions_mean': result['chill_portions'].get('mean'),
        'window_source': windows['source'], 'unconstrained': windows.get('unconstrained', False),
        'clock_reasons': (result.get('chill_clock') or {}).get('reasons'),
        'calendar': {k: result['calendar'][k].get('median_date') for k in ('budbreak', 'flowering_start', 'flowering_end',
                                                                          'harvest_start', 'harvest_end')},
        'windows': {'bloom': windows['bloom'][0], 'harvest': windows['harvest'][0], 'planting_r_rule': planting},
        'bloom': overlap(windows['bloom'][0], site['bloom_months'], windows['bloom'][1]),
        'harvest': overlap(windows['harvest'][0], site['harvest_months'], windows['harvest'][1]),
        'peak_harvest': overlap(windows['harvest'][0], site['peak_harvest_months'], windows['harvest'][1]),
        'r_planting_rule': overlap(planting, site.get('planting_months') or []) if budbreak else None,
        'ranked_risks': [r['risk'] for r in result['risks']['ranked']],
        'managed_recurring': (result.get('managed_cycle') or {}).get('favourable', {}).get('recurring'),
    }


def summarize(records):
    """Per region and profile. Chill-clock and managed-cycle windows are summarised separately with their own n."""
    mean = lambda values: float(np.mean(values)) if values else None
    groups = {g: [r for r in records if r['group'] == g] for g in sorted({r['group'] for r in records})}
    groups['All sites growing southern highbush'] = [r for r in records if 'SHB' in r['species']]
    out = {}
    for group, members in groups.items():
        members = [r for r in members if r['status'] == 'assessed']
        out[group] = {'sites': len(members)}
        for name in COMPARED:
            rows = [r['profiles'][name] for r in members]
            scores = [x['system_score'] for x in rows if x['system_score'] is not None]
            clock = [x for x in rows if x['window_source'] == 'chill_clock']
            managed = [x for x in rows if x['window_source'] == 'managed_cycle']
            field = lambda subset, stage, key: mean([x[stage][key] for x in subset
                                                      if x[stage] and x[stage].get(key) is not None])
            out[group][name] = {
                'system_scored': len(scores), 'system_mean_score': mean(scores),
                'system_exact': sum(s == 1.0 for s in scores), 'no_window': sum(x['window_source'] is None for x in rows),
                'clock_sites': len(clock),
                'clock_bloom_midpoint_inside': field(clock, 'bloom', 'midpoint_inside'),
                'clock_harvest_midpoint_inside': field(clock, 'harvest', 'midpoint_inside'),
                'clock_harvest_gap_months': field(clock, 'harvest', 'midpoint_gap_months'),
                'clock_harvest_recall': field(clock, 'harvest', 'recall'),
                'clock_harvest_precision': field(clock, 'harvest', 'precision'),
                'managed_sites': len(managed), 'managed_unconstrained': sum(x['unconstrained'] for x in managed),
                'managed_empty': sum(not x['windows']['harvest'] for x in managed),
                'managed_harvest_recall': field(managed, 'harvest', 'recall'),
                'managed_harvest_precision': field(managed, 'harvest', 'precision'),
                'planting_assessed': sum(x['r_planting_rule'] is not None for x in clock),
                'planting_recall': field(clock, 'r_planting_rule', 'recall'),
                'planting_precision': field(clock, 'r_planting_rule', 'precision')}
    return out


def months(values):
    return ', '.join(MONTHS[m - 1] for m in values) if values else 'none'


def render(report):
    style = ('body{font:15px system-ui;max-width:1320px;margin:32px auto;padding:0 20px;color:#1d1d1f}'
             'table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:6px 8px;border-bottom:1px solid #d6d6d6;'
             'text-align:left;vertical-align:top}.scroll{overflow:auto}.k{color:#555;font-size:13px}h2{margin-top:36px}')
    parts = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
             f'<title>Literature benchmark</title><style>{style}</style></head><body>',
             '<h1>Model versus published regional practice</h1>',
             f'<p class="k">{html.escape(report["method"])} · production method {html.escape(report["production_method"])} · '
             f'{len(report["sites"])} sites · compiled expectations are regional literature, not field observations of these grid cells.</p>',
             '<ul>' + ''.join(f'<li>{html.escape(x)}</li>' for x in report['caveats']) + '</ul>',
             '<h2>Summary by region</h2>']
    rows = []
    pct = lambda v: '–' if v is None else f'{100 * v:.0f}%'  # no sites in the subset
    for group, s in report['summary'].items():
        for name in COMPARED:
            v = s[name]
            rows.append([group, name, s['sites'], f"{v['system_exact']}/{v['system_scored']}", v['system_mean_score'],
                         v['clock_sites'], pct(v['clock_bloom_midpoint_inside']), pct(v['clock_harvest_midpoint_inside']),
                         '–' if v['clock_harvest_gap_months'] is None else round(v['clock_harvest_gap_months'], 1),
                         pct(v['clock_harvest_recall']), pct(v['clock_harvest_precision']),
                         f"{v['managed_sites']} ({v['managed_unconstrained']} unconstrained, {v['managed_empty']} empty)",
                         pct(v['managed_harvest_recall']),
                         pct(v['managed_harvest_precision']), v['no_window'],
                         f"{pct(v['planting_recall'])} / {pct(v['planting_precision'])} (n={v['planting_assessed']})"
                         if v['planting_assessed'] else '–'])
    parts.append(table(['Region', 'Profile', 'Sites', 'System exact', 'System score', 'Chill-clock sites',
                        'Bloom midpoint in published months', 'Harvest midpoint in published months', 'Harvest midpoint gap (months)',
                        'Harvest recall', 'Harvest precision', 'Managed-cycle sites', 'Managed harvest recall',
                        'Managed harvest precision', 'No window', 'R planting rule recall / precision'], rows))
    parts.append('<p class="k">System score: 1 same class, 0.5 adjacent class or no two-thirds majority, 0 opposite; mixed practice '
                 'counts as semi-evergreen. Chill-clock rows use the median modelled window and need at least 12 winters with a '
                 'calendar for every profile; midpoint shares are the fraction of sites whose window midpoint falls in a published '
                 'month, and the gap is the mean circular distance in months. Recall: share of published months covered by modelled '
                 'months; precision: share of modelled months that are published. Managed cycles report the union of favourable '
                 'start windows; an empty favourable window scores recall 0. The R planting rule (105 to 30 days before median '
                 'budbreak) is tested against published planting months, not adopted.</p>')
    for group in (g for g in report['summary'] if any(r['group'] == g for r in report['sites'])):
        parts.append(f'<h2>{html.escape(group)}</h2>')
        members = sorted((r for r in report['sites'] if r['group'] == group), key=lambda r: -r['lat'])
        body = []
        for r in members:
            published = [r['name'], f"{r['lat']:.2f}",
                         f"{r['production_system']} · {', '.join(r['species'])} · {r['protection'].replace('_', ' ')}",
                         months(r['bloom_months']) if r['bloom_months'] else 'not published', months(r['harvest_months'])]
            if r['status'] != 'assessed':
                body.append(published + [r['status']] + [''] * 5 + [r['confidence']])
                continue
            cells = published
            for name in COMPARED:
                x = r['profiles'][name]
                source = {'managed_cycle': 'managed', 'chill_clock': 'chill clock', None: 'no window'}[x['window_source']]
                cells += [f"{x['system']} ({x['system_score']})",
                          f"{months(x['windows']['bloom'])} [{source}]", months(x['windows']['harvest'])]
            body.append(cells + [r['confidence']])
        parts.append(table(['Site', 'Lat', 'Published system · species · protection', 'Published bloom', 'Published harvest',
                            'v2 system', 'v2 bloom', 'v2 harvest', 'v3 system', 'v3 bloom', 'v3 harvest', 'Evidence'], body))
    parts.append('<h2>Sources</h2><ul>')
    for r in report['sites']:
        links = '; '.join(f'<a href="{html.escape(s["url"], quote=True)}">{html.escape(s["title"])}</a> ({html.escape(s["access"])})'
                          for s in r['sources'])
        parts.append(f'<li><strong>{html.escape(r["name"])}</strong>: {links}</li>')
    parts.append('</ul></body></html>')
    return '\n'.join(parts)


CAVEATS = [
    'Published months describe regional practice across cultivars, management and years; the model uses one 0.5 x 0.625 degree grid cell with one UF-type low-chill southern-highbush parameter set.',
    'Northern-highbush and rabbiteye regions are included to expose transfer limits; disagreement there can reflect species differences rather than weather errors.',
    'Grid minimum temperatures run warm against stations in earlier pilots, so chill and freeze are likely undercounted, most at deciduous and high-elevation sites.',
    'The model assumes open field. Where tunnels are common (protection column), published harvest starts earlier and runs longer than open-field weather implies.',
    'Expectations were compiled from sources before comparison and were not tuned to the model. They are not independent field validation.',
]


def run(root=ROOT, registry=REGISTRY):
    sites = json.loads(Path(registry).read_text())['sites']
    land = LandMask(root)
    records = []
    for site in sites:
        record = {**site, 'status': 'assessed', 'profiles': {}}
        daily, provenance = extract(root, site['lat'], site['lon'], land, padding=True)
        if daily is None:
            record['status'] = 'unsupported_location'
            records.append(record)
            continue
        try:
            hourly, source = hourly_for(site['lat'], site['lon'], root)
        except RuntimeError as error:
            hourly, source, record['hourly_error'] = None, None, str(error)
        if hourly is None:
            record['status'] = 'hourly_unavailable'
            records.append(record)
            continue
        record['hourly_source'] = {k: source.get(k) for k in ('source_lat', 'source_lon', 'distance_km')}
        record['daily_distance_km'] = provenance['sources'][0].get('distance_km') if provenance.get('sources') else None
        daily = daily.set_index('time')
        for name in COMPARED:
            record['profiles'][name] = assess(site, hourly, daily, name)
        records.append(record)
        print(json.dumps({'site': site['id'], **{n: [p['system'], p['window_source'], p['windows']['bloom'],
                                                     p['windows']['harvest']] for n, p in record['profiles'].items()}}),
              flush=True)
    report = {'method': 'literature-benchmark-v1', 'production_method': METHOD, 'profiles': list(COMPARED),
              'registry_sha256': hashlib.sha256(Path(registry).read_bytes()).hexdigest(),
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'caveats': CAVEATS, 'summary': summarize(records), 'sites': records}
    out = root / 'reports/benchmark'
    write_json(out / 'benchmark.json', report)
    (out / 'benchmark.html').write_text(render(report))
    print(json.dumps(report['summary'], indent=1))


if __name__ == '__main__':
    run(registry=sys.argv[1] if len(sys.argv) > 1 else REGISTRY)
