"""Reproducible, offline climate evidence: no cultivar or phenology predictions."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import numpy as np
import pandas as pd
from postprocess import ROOT, LandMask, extract
from discover import write_json


def complete(series, start, end, freq):
    expected=pd.date_range(start,end,freq=freq,inclusive='left')
    if series.index.has_duplicates:
        raise ValueError('Duplicate timestamps')
    values=series.reindex(expected)
    return values if len(values) and np.isfinite(values.to_numpy()).all() else None


def chill(series,start,end):
    values=complete(series,start,end,'h')
    return None if values is None else int(((values>=0)&(values<=7.2)).sum())


def dry_spell(series,start,end):
    values=complete(series,start,end,'D')
    if values is None or (values<0).any() or (values>1000).any():
        return None
    longest=run=0
    for dry in values<1:
        run=run+1 if dry else 0
        longest=max(longest,run)
    return longest


def stat(values,operation):
    a=np.asarray(values,dtype=float)
    if not len(a) or not np.isfinite(a).all(): return None
    return float(getattr(np,operation)(a))


def chart(title,series,labels,ylabel):
    colors=['#176b65','#bf632b','#5559a7']
    allvalues=[v for values in series.values() for v in values if v is not None]
    if not allvalues:return '<p>No valid chart values.</p>'
    low=min(0,min(allvalues)); high=max(allvalues); span=max(high-low,1)
    left,top,width,height=65,25,660,190
    parts=[f'<figure><h3>{html.escape(title)}</h3><svg viewBox="0 0 760 265" role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title>']
    for step in range(5):
        value=low+span*step/4; y=top+height-height*step/4
        parts.append(f'<path d="M{left} {y}h{width}" stroke="#dce3df"/><text x="55" y="{y+4}" text-anchor="end">{value:.1f}</text>')
    for i,label in enumerate(labels):
        x=left+i*width/max(len(labels)-1,1)
        parts.append(f'<text x="{x}" y="235" text-anchor="middle">{html.escape(str(label))}</text>')
    for color,(name,values) in zip(colors,series.items()):
        segment=[]
        for i,value in enumerate(values):
            if value is None:
                if segment:parts.append(f'<polyline points="{" ".join(segment)}" fill="none" stroke="{color}" stroke-width="2.5"/>')
                segment=[];continue
            x=left+i*width/max(len(labels)-1,1); y=top+height-(value-low)/span*height
            segment.append(f'{x},{y}')
            parts.append(f'<circle cx="{x}" cy="{y}" r="3" fill="{color}"><title>{html.escape(name)}: {value:.2f}</title></circle>')
        if segment:parts.append(f'<polyline points="{" ".join(segment)}" fill="none" stroke="{color}" stroke-width="2.5"/>')
    parts.append('</svg><figcaption>'+html.escape(ylabel)+' · '+ ' / '.join(f'<span style="color:{c}">{html.escape(n)}</span>' for c,n in zip(colors,series))+'</figcaption></figure>')
    return ''.join(parts)


def table(headers,rows):
    def cell(v):return 'unavailable' if v is None else f'{v:.1f}' if isinstance(v,float) else html.escape(str(v))
    return '<div class="scroll"><table><thead><tr>'+''.join(f'<th>{html.escape(h)}</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{cell(v)}</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'


def build(root):
    sites=[s for s in json.loads((root/'config/sites.json').read_text()) if s['name'] in ('Papanduva','Citra','Waldo')]
    sites.sort(key=lambda s:['Papanduva','Citra','Waldo'].index(s['name']))
    land=LandMask(root); result={}
    for site in sites:
        frame,provenance=extract(root,site['lat'],site['lon'],land)
        if frame is None:raise ValueError('Demo site unsupported')
        frame=frame.set_index('time')
        hourlypath=root/'data/normalized/pilot/pilot'/site['id']/'met_hourly.parquet'
        hourly=pd.read_parquet(hourlypath).set_index('time').tmean_c
        annual=[];monthly=[]
        for year in range(2011,2026):
            block=frame.loc[str(year)]; start=f'{year}-01-01'; end=f'{year+1}-01-01'
            rain=complete(block.precip_mm,start,end,'D')
            rain_ok=rain is not None and not ((rain<0)|(rain>1000)).any()
            cstart,cend=(f'{year}-05-01',f'{year}-09-01') if site['lat']<0 else (f'{year-1}-11-01',f'{year}-03-01')
            annual.append({'year':year,'tmean':stat(block.tmean_c,'mean'),'rain_mm':float(rain.sum()) if rain_ok else None,
                'wet_days':int((rain>=1).sum()) if rain_ok else None,'dry_spell':dry_spell(block.precip_mm,start,end),
                'cold_days':int((block.tmin_c<0).sum()) if complete(block.tmin_c,start,end,'D') is not None else None,
                'hot_days':int((block.tmax_c>=35).sum()) if complete(block.tmax_c,start,end,'D') is not None else None,
                'chill_hours':chill(hourly,cstart,cend),'chill_start':cstart,'chill_end_exclusive':cend})
            for month in range(1,13):
                b=block[block.index.month==month]
                p=b.precip_mm; ok=np.isfinite(p).all() and not ((p<0)|(p>1000)).any()
                monthly.append({'year':year,'month':month,'tmean':stat(b.tmean_c,'mean'),
                    'rain_mm':float(p.sum()) if ok else None,'solar':stat(b.shortwave_mj_m2_day,'mean')})
        climate={field:[stat([r[field] for r in monthly if r['month']==m],'mean') for m in range(1,13)] for field in ['tmean','rain_mm','solar']}
        result[site['name']]={'site':site,'provenance':provenance,'hourly_sha256':hashlib.sha256(hourlypath.read_bytes()).hexdigest(),
                            'annual':annual,'monthly':monthly,'climatology':climate}
    report=root/'reports/climate_evidence';report.mkdir(parents=True,exist_ok=True)
    write_json(report/'climate_evidence.json',{'method_version':'climate-evidence-v1','sites':result})
    parts=['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Climate evidence | Papanduva, Citra & Waldo</title>
<style>body{font:16px/1.6 system-ui,sans-serif;color:#213d36;background:#f3f6f2;margin:0}main{max-width:1080px;margin:auto;padding:40px 28px}header{border-bottom:4px solid #176b65;padding:24px 0}h1{font-size:42px;line-height:1.15;max-width:850px}h2{margin-top:48px}h3{margin:0 0 14px}p{max-width:900px}.eyebrow{letter-spacing:.15em;font-size:12px;font-weight:700}figure,.panel{background:white;padding:24px;margin:20px 0;border:1px solid #dce3df;border-radius:12px}svg{width:100%;max-height:360px}svg text{font:11px system-ui;fill:#465c54}figcaption{font-size:13px}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:right;padding:10px;border-bottom:1px solid #dce3df}th:first-child,td:first-child{text-align:left}th{background:#e8efea}.notice{border-left:4px solid #bf632b;padding:12px 20px;background:#fff8ec}a{color:#176b65}@media print{body{background:white}main{padding:0}figure{break-inside:avoid}h2{break-after:avoid}}</style><main><header><div class="eyebrow">RESEARCH DEMONSTRATION · PART 1 / EARLY PART 2</div><h1>From downloaded weather<br>to climate evidence</h1><p>Papanduva, Brazil · Citra and Waldo, Florida<br>2011–2025 baseline · NASA POWER native-grid estimates</p></header>
<p class="notice">This report describes climate exposure, not cultivar suitability, crop damage, yield or a recommended production calendar. No cultivar data or trained recommendation model is used.</p>
<h2>01 / What has actually been downloaded?</h2><p>The global daily archive completed all 7,257 planned tiles for 2010–2025. Eight fields cover temperature, rain, humidity, wind, dewpoint and sunlight. Meteorology remains at 0.5° latitude × 0.625° longitude; solar remains at 1° × 1°. Hourly temperature and dewpoint exist for 14 pilot locations—not the whole globe. The 2010 buffer supports cross-year seasons.</p>''']
    parts.append(table(['Location','Daily baseline rows','Missing weather values','Suspect rain days','Met. cell distance km'],[[n,r['provenance']['rows'],sum(q.get('missing',0) for q in r['provenance']['qc'].values()),r['provenance']['screening']['precip_suspect_days'],r['provenance']['sources'][0]['distance_km']] for n,r in result.items()]))
    parts.append('<h2>02 / The seasonal pattern</h2><p>Calendar months show when conditions occur. These are means across 15 separate years, not observations from one typical year. Rainfall is mean monthly total; sunlight is mean daily energy.</p>')
    months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    for field,title,unit in [('tmean','Monthly mean temperature','°C'),('rain_mm','Monthly rainfall','mm/month'),('solar','Daily solar energy by month','MJ/m²/day')]:
        parts.append(chart(title,{n:r['climatology'][field] for n,r in result.items()},months,unit))
    parts.append('<h2>03 / Compare like seasons—not January to January</h2><p>Exploratory meteorological alignment: winter is Dec–Feb in Florida and Jun–Aug in Brazil; spring is Mar–May / Sep–Nov, summer Jun–Aug / Dec–Feb, autumn Sep–Nov / Mar–May. This is a hemisphere alignment, not a blueberry growth-stage calendar.</p>')
    rows=[]
    for name,r in result.items():
        seasons=[[6,7,8],[9,10,11],[12,1,2],[3,4,5]] if r['site']['lat']<0 else [[12,1,2],[3,4,5],[6,7,8],[9,10,11]]
        for label,ms in zip(['Winter','Spring','Summer','Autumn'],seasons):
            rows.append([name,label,float(np.mean([r['climatology']['tmean'][m-1] for m in ms])),float(np.sum([r['climatology']['rain_mm'][m-1] for m in ms]))])
    parts.append(table(['Location','Season','Mean of monthly temperatures °C','Sum of monthly climatological rain mm'],rows))
    parts.append('<h2>04 / Every year is different</h2><p>Chill uses the inclusive 0–7.2°C band. Florida: November of the previous year through February, labelled by ending year; Brazil: May–August of the labelled year. All timestamps and boundaries are UTC. These are provisional four-month reference windows, not equivalent-length biological seasons, and not Chill Portions. A missing hour makes the whole chill-window total unavailable.</p>')
    for field,title,unit in [('chill_hours','Bounded chill hours by reference winter','hours in 0–7.2°C'),('rain_mm','Annual rainfall variability','mm/year'),('dry_spell','Longest within-year dry spell','consecutive days with rain <1 mm')]:
        parts.append(chart(title,{n:[a[field] for a in r['annual']] for n,r in result.items()},list(range(2011,2026)),unit))
    parts.append('<p>Dry spells are truncated at calendar-year boundaries. Missing, negative or suspect extreme rainfall makes the corresponding window unavailable. Annual rain is context only—not harvest rain. Cold means Tmin &lt;0°C; hot means Tmax ≥35°C. These illustrative thresholds do not measure plant-stage damage.</p>')
    for name,r in result.items():
        parts.append('<h3>'+html.escape(name)+'</h3>'+table(['Year','Mean °C','Rain mm','Wet days ≥1mm','Max dry spell','Days <0°C','Days ≥35°C','Chill hours'],[[a[k] for k in ['year','tmean','rain_mm','wet_days','dry_spell','cold_days','hot_days','chill_hours']] for a in r['annual']]))
    parts.append('''<h2>05 / How much should we trust these numbers?</h2><p>The 2020 observation pilot found grid minimum temperatures averaging 0.95°C warmer at FAWN Citra (224 complete accepted days), 0.90°C warmer at INMET Major Vieira and 1.33°C warmer at Rio Negrinho (365 days each). Both Brazilian comparisons missed three observed below-zero days. These are small, screened samples; no correction has been fitted. They warn against treating gridded cold exposure as field-level frost prediction.</p><p>Citra uses provider quality flags; the INMET pilot has only coarse numeric screening. Station daily boundaries were aligned to UTC, including INMET preceding-hour extrema. Citra sampled extrema may miss between-sample extremes. Rainfall validation remains provisional. Nearby stations are not measurements of the target field.</p>
<h2>06 / What this enables next</h2><p>Use these patterns to ask focused questions about seasonal chill, cold exposure, wet periods and dry spells. Next: test more station-years and review reference windows with the supervisor. Cultivar rankings, production-system classifications and flowering/harvest predictions remain deferred.</p>
<h2>Methods & provenance</h2><p>Daily series are extracted from the completed global archive. Hourly series are taken from the stored pilot archive. No weather payload is downloaded by this script. Source coordinates, units, checksums, coverage, annual results and 180 monthly summaries per site are in the companion JSON. Indicators require complete windows; no interpolation or bias correction is used. Seasonal temperature table weights each monthly mean equally. Method: climate-evidence-v1.</p><p><a href="https://power.larc.nasa.gov/docs/services/aws/">NASA POWER bulk documentation</a> · <a href="https://fawn.ifas.ufl.edu/data/fawn_data_qaqc_pub/">FAWN quality-flagged observations</a> · <a href="https://portal.inmet.gov.br/dadoshistoricos">INMET historical observations</a></p><p>Reproduce on the project server: <code>env/bin/python code/evidence_report.py</code>. Output: <code>reports/climate_evidence/</code>.</p></main></html>''')
    (report/'climate_evidence.html').write_text(''.join(parts))
    print(json.dumps({'report':str(report/'climate_evidence.html'),'sites':{n:{'chill_median':float(np.median([a['chill_hours'] for a in r['annual']])),'rain_mean':float(np.mean([a['rain_mm'] for a in r['annual']]))} for n,r in result.items()}}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT)
    build(parser.parse_args().root)
