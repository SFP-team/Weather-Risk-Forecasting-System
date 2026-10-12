"""ODEPA comercio exterior: Chilean fresh blueberry exports by month, region of origin and destination.

Tariff lines confirmed in the yearly CSVs (code and ODEPA description):
- 08104000 'Arándanos rojos, azules, mirtilos y demás frutos del género Vaccinium (total)', 1998 to 2006: all Vaccinium.
- 08104020 'Arándanos azules o blueberry, frescos (desde 2007)', 2007 to 2011.
- 08104021 organic and 08104029 other 'arándanos azules o blueberry, frescos', 2012 onward.
`line_scope` keeps the pre-2007 all-Vaccinium line apart so users can drop it.
Licence CC BY (CKAN package licence): cite ODEPA and Servicio Nacional de Aduanas.
"""
import re
import pandas as pd
from ..runner import Request
from .odepa_catastro import ckan_resources,fold,number,read_csv,year_of

JOB={'id':'odepa-exports','source_ids':['cl-odepa-comercio-exterior'],'schedule':'monthly',
     'description':'ODEPA yearly export CSVs (1998 onward), fresh blueberry tonnes and USD FOB by month, region and destination',
     'max_bytes_per_run':600_000_000,'derived_only':False}
PACKAGE='https://datos.odepa.gob.cl/api/3/action/package_show?id=comercio-exterior'
BLUEBERRY={'08104020':'blueberry','08104021':'blueberry','08104029':'blueberry','08104000':'vaccinium_total'}
COLUMNS={'anio':'year','mes':'month','codigo producto':'code','producto':'product','id region':'region_id',
         'region origen':'region','pais destino':'destination','unidad':'unit','volumen':'volume','usd fob':'usd_fob'}

def line_scope(code,product):
    """Classify a tariff line; a new blueberry code is caught by its description inside heading 0810.40."""
    if code in BLUEBERRY: return BLUEBERRY[code]
    p=fold(product)
    if code.startswith('081040') and ('blueberr' in p or 'azul' in p) and 'congel' not in p and 'sec' not in p: return 'blueberry'
    return None

def blueberry_rows(raw):
    df=raw.rename(columns={c:COLUMNS[fold(c)] for c in raw.columns if fold(c) in COLUMNS})
    missing=set(COLUMNS.values())-set(df.columns)
    if missing: raise ValueError(f'export CSV lacks columns {sorted(missing)}')
    df['code']=df['code'].str.strip().str.zfill(8)
    df=df[df['code'].str.startswith('081040')].copy()
    df['line_scope']=[line_scope(c,p) for c,p in zip(df['code'],df['product'])]
    df=df[df['line_scope'].notna()].copy()
    for c in ('year','month','region_id'): df[c]=number(df[c]).astype('Int64')
    for c in ('volume','usd_fob'): df[c]=number(df[c])
    df['organic']=df['code'].eq('08104021')
    # Volumes are net kilos for these lines; any other unit is kept with value but without tonnes.
    df['tonnes']=df['volume'].where(df['unit'].map(fold).eq('kilo neto'))/1000
    for c in ('region','destination','unit','product'): df[c]=df[c].str.strip()
    return df[['year','month','code','line_scope','organic','product','region_id','region','destination','unit','volume','tonnes','usd_fob']]

def plan(ctx):
    meta=ctx.fetch(Request('package',PACKAGE,filename='package_show.json',max_bytes=5_000_000))
    if not meta.path: raise RuntimeError(f'CKAN package metadata unavailable ({meta.status})')
    reqs=[]
    for r in ckan_resources(meta.path)['resources']:
        y=year_of(r)
        if (r.get('format') or '').upper()=='CSV' and y and fold(r.get('name') or '').startswith('exportaciones'):
            reqs.append(Request(f'exports_{y}',r['url'],filename=f'comex_exportacion_{y}.csv',max_bytes=100_000_000))
    if not reqs: raise RuntimeError('no yearly export CSV resources listed in the CKAN package')
    return reqs

def parse(ctx,assets):
    frames,missing=[],[]
    for key,a in sorted(assets.items()):
        if not key.startswith('exports_'): continue
        if not a.path: missing.append(key); continue
        frames.append(blueberry_rows(read_csv(a.path)))
    if not frames: raise RuntimeError('no export CSV could be read')
    rows=pd.concat(frames,ignore_index=True)
    keys=['year','month','code','line_scope','organic','region_id','region','destination','unit']
    rows=rows.groupby(keys,dropna=False).agg(product=('product','first'),volume=('volume','sum'),
                                             tonnes=('tonnes',lambda s:s.sum(min_count=1)),usd_fob=('usd_fob','sum')).reset_index()
    rows=rows.sort_values(keys).reset_index(drop=True)
    ctx.write_table('exports_blueberry_monthly',rows)
    by_region=rows.groupby(['year','month','line_scope','region_id','region'],dropna=False)[['tonnes','usd_fob']].sum(min_count=1).reset_index()
    ctx.write_table('exports_blueberry_region_monthly',by_region)
    return {'rows':len(rows),'region_month_rows':len(by_region),'years':[int(rows['year'].min()),int(rows['year'].max())],
            'codes':{c:int(n) for c,n in rows['code'].value_counts().sort_index().items()},'unreadable':missing}
