"""Controlled chill sensitivity on our UTC archive, not a rerun of Paul's R."""
import json
import pandas as pd
from postprocess import ROOT
from evidence_report import complete
from discover import write_json


def counts(values):
    return {'bounded_inclusive':int(((values>=0)&(values<=7.2)).sum()),
            'below_only_strict':int((values<7.2).sum()),
            'below_zero':int((values<0).sum()),'exact_upper':int((values==7.2).sum())}


def run():
    sites=json.loads((ROOT/'config/sites.json').read_text())
    results=[]
    for site in sites:
        if site['name'] not in ('Papanduva','Citra','Waldo'):continue
        series=pd.read_parquet(ROOT/'data/normalized/pilot/pilot'/site['id']/'met_hourly.parquet').set_index('time').tmean_c
        for year in range(2011,2026):
            if site['lat']<0:
                short=(f'{year}-05-01',f'{year}-09-01');long=(f'{year}-04-01',f'{year}-10-01');paul_label=year+1
            else:
                short=(f'{year-1}-11-01',f'{year}-03-01');long=(f'{year-1}-11-01',f'{year}-05-01');paul_label=year
            a,b=complete(series,*short,'h'),complete(series,*long,'h')
            if a is None or b is None:raise ValueError('Incomplete sensitivity window')
            ca,cb=counts(a),counts(b)
            assert ca['below_only_strict']-ca['bounded_inclusive']==ca['below_zero']-ca['exact_upper']
            results.append({'site':site['name'],'demo_year':year,'paul_crop_year_label':paul_label,
                'short_start':short[0],'short_end_exclusive':short[1],
                'long_start':long[0],'long_end_exclusive':long[1],
                'short':ca,'long':cb})
    summary=[]
    for name in ('Papanduva','Citra','Waldo'):
        rows=[r for r in results if r['site']==name]
        means={f'{window}_{method}':sum(r[window][method] for r in rows)/len(rows)
               for window in ('short','long') for method in ('bounded_inclusive','below_only_strict')}
        summary.append({'site':name,**means,
            'window_effect_bounded':means['long_bounded_inclusive']-means['short_bounded_inclusive'],
            'definition_effect_long':means['long_below_only_strict']-means['long_bounded_inclusive']})
    report={'method':'controlled-UTC-chill-sensitivity-v1','summary':summary,'annual':results,
        'limitations':['Same stored UTC data and 15 aligned winters; not original LST data or original historical baseline.',
            'South 2011–2025 winters map to Paul crop-year labels 2012–2026; do not join by label alone.',
            'No R execution, Dynamic Model, production classifier or stage-risk replication performed.',
            'Means are compared with means; supervisor demonstration charts also report medians separately.']}
    write_json(ROOT/'reports/method_reconciliation.json',report)
    print(json.dumps(summary))


if __name__=='__main__':run()
