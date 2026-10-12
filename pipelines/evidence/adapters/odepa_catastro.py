"""CIREN-ODEPA fruit orchard census (catastro frutícola): blueberry blocks by commune and variety.

Each yearly CSV covers the regions surveyed that year, so the latest survey differs by region.
Licence CC BY (CKAN package licence): cite ODEPA-CIREN.
"""
import json,re,unicodedata
import pandas as pd
from ..runner import Request

JOB={'id':'odepa-catastro','source_ids':['cl-odepa-catastro-fruticola'],'schedule':'quarterly',
     'description':'CIREN-ODEPA orchard census CSVs (1999 onward), blueberry blocks and commune by variety summary',
     'max_bytes_per_run':400_000_000,'derived_only':False}
PACKAGE='https://datos.odepa.gob.cl/api/3/action/package_show?id=catastro-fruticola'
COLUMNS={'anio':'survey_year','id region':'region_id','region':'region','provincia':'province','comuna':'commune',
         'numero explotacion':'farm_no','numero bloque':'block_no','tipo productor':'producer_type','especie':'species',
         'variedad':'variety','anio plantacion':'planting_year','metodo de riego':'irrigation',
         'numero de arboles':'plants','superficie (ha)':'area_ha'}

def fold(s):
    """Lower case, strip accents and collapse spaces, so 'ARÁNDANO  americano' matches 'arandano americano'."""
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()
    return re.sub(r'\s+',' ',s).strip()

def is_blueberry(species):
    # Chile records highbush blueberry as 'Arándano Americano'; cranberry ('arándano rojo') is not grown commercially
    # but would share the stem, so it is excluded explicitly.
    f=fold(species)
    return f.startswith('arandano') and not any(w in f for w in ('rojo','cranberry'))

def number(s):
    """Parse Chilean numbers: decimal comma, optional dot thousands separator."""
    s=s.astype('string').str.strip().str.replace('\u00a0','',regex=False)
    s=s.where(~s.str.contains(',',na=False),s.str.replace('.','',regex=False).str.replace(',','.',regex=False))
    return pd.to_numeric(s,errors='coerce')

def ckan_resources(path):
    meta=json.loads(path.read_text(encoding='utf-8'))
    if not meta.get('success'): raise ValueError('CKAN package_show did not report success')
    return meta['result']

def year_of(resource):
    m=re.search(r'(19|20)\d{2}',(resource.get('name') or '')+' '+(resource.get('url') or ''))
    return int(m.group(0)) if m else None

def read_csv(path):
    for enc in ('utf-8-sig','latin-1'):
        try: return pd.read_csv(path,dtype=str,encoding=enc,keep_default_na=False)
        except UnicodeDecodeError: continue
    raise ValueError(f'cannot decode {path}')

def blueberry_blocks(raw):
    """Normalise one survey CSV and keep blueberry rows only."""
    df=raw.rename(columns={c:COLUMNS[fold(c)] for c in raw.columns if fold(c) in COLUMNS})
    missing=set(COLUMNS.values())-set(df.columns)-{'region_id'}
    if missing: raise ValueError(f'catastro CSV lacks columns {sorted(missing)}')
    df=df[df['species'].map(is_blueberry)].copy()
    for c in ('survey_year','region_id','planting_year','plants','area_ha'):
        if c in df: df[c]=number(df[c])
    for c in ('survey_year','region_id','planting_year','plants'):
        if c in df: df[c]=df[c].astype('Int64')
    for c in ('region','province','commune','farm_no','block_no','producer_type','species','variety','irrigation'):
        df[c]=df[c].str.strip()
    return df[[c for c in COLUMNS.values() if c in df]].reset_index(drop=True)

def summarise(blocks):
    g=blocks.groupby(['survey_year','region','commune','variety'],dropna=False)
    out=g.agg(area_ha=('area_ha','sum'),blocks=('block_no','size'),farms=('farm_no','nunique'),plants=('plants','sum')).reset_index()
    return out.sort_values(['survey_year','region','commune','area_ha'],ascending=[True,True,True,False]).reset_index(drop=True)

def plan(ctx):
    meta=ctx.fetch(Request('package',PACKAGE,filename='package_show.json',max_bytes=5_000_000))
    if not meta.path: raise RuntimeError(f'CKAN package metadata unavailable ({meta.status})')
    reqs=[]
    for r in ckan_resources(meta.path)['resources']:
        y=year_of(r)
        if (r.get('format') or '').upper()=='CSV' and y:
            reqs.append(Request(f'csv_{y}',r['url'],filename=f'catastro_fruticola_{y}.csv',max_bytes=100_000_000))
    if not reqs: raise RuntimeError('no yearly CSV resources listed in the CKAN package')
    return reqs

def parse(ctx,assets):
    frames,species,missing=[],{},[]
    for key,a in sorted(assets.items()):
        if not key.startswith('csv_'): continue
        if not a.path: missing.append(key); continue
        raw=read_csv(a.path)
        col=next((c for c in raw.columns if fold(c)=='especie'),None)
        if col:
            for s,n in raw[col].value_counts().items():
                if is_blueberry(s): species[s]=species.get(s,0)+int(n)
        frames.append(blueberry_blocks(raw))
    if not frames: raise RuntimeError('no catastro CSV could be read')
    blocks=pd.concat(frames,ignore_index=True)
    ctx.write_table('catastro_blueberry_blocks',blocks)
    summary=summarise(blocks)
    ctx.write_table('catastro_blueberry_summary',summary)
    latest=blocks.groupby('region')['survey_year'].max().astype(int).to_dict()
    return {'blocks':len(blocks),'summary_rows':len(summary),'survey_years':sorted(int(y) for y in blocks['survey_year'].dropna().unique()),
            'blueberry_species_names':species,'latest_survey_by_region':latest,'unreadable':missing}
