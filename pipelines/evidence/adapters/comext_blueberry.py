"""Eurostat Comext DS-045409: monthly EU imports of CN 0810 40 50 by reporter and partner, from 2010.

CN 0810 40 50 is 'fresh fruit of Vaccinium macrocarpon and Vaccinium corymbosum': highbush blueberry and
American cranberry share the line, so it is not blueberry-only. Arrivals from southern-hemisphere and
tropical origins are almost all blueberries, but intra-EU and North American flows may carry cranberries.

Query size: the API answers synchronously below 500,000 cells and refuses above 5,000,000
(Eurostat 'API - Detailed guidelines - Asynchronous API'). One request per reporter is at most
22 partners x 2 indicators x about 210 months, under 10,000 cells, so every request stays synchronous.
Eurostat copyright notice: reuse authorised provided the source is acknowledged.
"""
import json
import pandas as pd
from ..runner import Request

JOB={'id':'comext-blueberry','source_ids':['eu-eurostat-comext-ds045409'],'schedule':'monthly',
     'description':'Eurostat Comext monthly imports of CN 08104050 (highbush blueberry and American cranberry) into the EU and main reporters',
     'max_bytes_per_run':50_000_000,'derived_only':False}
API='https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409'
PRODUCT='08104050'
CAVEAT=('CN 08104050 covers fresh Vaccinium corymbosum (highbush blueberry) and Vaccinium macrocarpon '
        '(American cranberry) together; it is not a blueberry-only line.')
REPORTERS=['EU27_2020','NL','DE','ES','FR','PL','IT','BE']
PARTNERS=['PE','CL','MA','ZA','ZW','NA','ZM','EG','MX','AR','UY','CO','RS','UA','GE','CN','PT','ES','US','CA','NZ','AU']
INDICATORS={'QUANTITY_IN_100KG':'quantity_100kg','VALUE_IN_EUROS':'value_eur'}
SINCE='2010-01'

def jsonstat_frame(doc):
    """Flatten a JSON-stat 2.0 dataset into one row per non-empty cell, with one column per dimension."""
    if 'value' not in doc or 'dimension' not in doc:
        # An over-sized query comes back as an asynchronous ticket or error object instead of data.
        raise ValueError(f'not a JSON-stat dataset: {json.dumps(doc)[:300]}')
    ids,size=doc['id'],doc['size']
    codes=[]
    for d in ids:
        idx=doc['dimension'][d]['category']['index']
        codes.append(sorted(idx,key=idx.get) if isinstance(idx,dict) else list(idx))
    vals=doc['value']
    items=vals.items() if isinstance(vals,dict) else ((i,v) for i,v in enumerate(vals) if v is not None)
    status=doc.get('status') or {}
    rows=[]
    for flat,v in items:
        flat=int(flat); rest=flat; pos=[]
        for n in reversed(size): pos.append(rest%n); rest//=n
        pos.reverse()
        row={d:codes[i][p] for i,(d,p) in enumerate(zip(ids,pos))}
        row['value']=v
        row['flag']=status.get(str(flat)) if isinstance(status,dict) else (status[flat] if flat<len(status) else None)
        rows.append(row)
    return pd.DataFrame(rows,columns=ids+['value','flag'])

def imports_table(doc):
    long=jsonstat_frame(doc)
    if long.empty: return pd.DataFrame(columns=['reporter','partner','product','year','month','period','quantity_100kg','tonnes','value_eur','flag'])
    long['indicators']=long['indicators'].map(INDICATORS)
    wide=long.pivot_table(index=['reporter','partner','product','flow','time'],columns='indicators',values='value',aggfunc='first').reset_index()
    flags=long.dropna(subset=['flag']).groupby(['reporter','partner','time'])['flag'].agg(lambda s:','.join(sorted(set(s))))
    wide=wide.merge(flags.rename('flag'),how='left',left_on=['reporter','partner','time'],right_index=True)
    for c in INDICATORS.values():
        if c not in wide: wide[c]=float('nan')
    wide['year']=wide['time'].str[:4].astype(int); wide['month']=wide['time'].str[5:7].astype(int)
    wide['tonnes']=wide['quantity_100kg']/10
    wide=wide.rename(columns={'time':'period'})
    return wide[['reporter','partner','product','year','month','period','quantity_100kg','tonnes','value_eur','flag']]

def plan(ctx):
    reqs=[]
    for r in REPORTERS:
        params={'format':'JSON','lang':'en','freq':'M','reporter':r,'partner':[p for p in PARTNERS if p!=r],
                'product':PRODUCT,'flow':'1','indicators':list(INDICATORS),'sinceTimePeriod':SINCE}
        reqs.append(Request(f'imports_{r}',API,params=params,filename=f'ds045409_{PRODUCT}_imports_{r}.json',max_bytes=20_000_000))
    return reqs

def parse(ctx,assets):
    frames,missing,updated=[],[],set()
    for key,a in sorted(assets.items()):
        if not a.path: missing.append(key); continue
        doc=json.loads(a.path.read_text(encoding='utf-8'))
        updated.add(doc.get('updated'))
        frames.append(imports_table(doc))
    if not frames: raise RuntimeError('no Comext response could be read')
    df=pd.concat(frames,ignore_index=True).sort_values(['reporter','partner','period']).reset_index(drop=True)
    df['cn_scope']='highbush blueberry and American cranberry (CN 08104050)'
    df.attrs.update({'caveat':CAVEAT,'source':'Eurostat Comext DS-045409','flow':'imports','quantity_unit':'100 kg','value_unit':'EUR'})
    ctx.write_table('comext_blueberry_monthly',df)
    return {'rows':len(df),'reporters':sorted(df['reporter'].unique()),'periods':[df['period'].min(),df['period'].max()],
            'eurostat_updated':sorted(u for u in updated if u),'caveat':CAVEAT,'missing':missing}
