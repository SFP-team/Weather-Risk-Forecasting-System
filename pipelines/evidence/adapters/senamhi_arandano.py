"""SENAMHI dekadal bulletin 'Pronóstico Agrometeorológico: Cultivo de Arándano' (August 2024 onward).

The bulletins page lists only the six newest PDFs, but the file numbers run from 1 without gaps
(02981SENA-1.pdf to -70.pdf on 2026-10-12), so the job backfills every number up to the newest listed.
File numbers are not in date order: numbers 1 to 4 are early 2025 and 5 to 14 are late 2024.
No licence or terms were found, so the text stays private research material.
"""
import calendar,datetime as dt,hashlib,os,re,subprocess
import pandas as pd
from ..runner import Request
from .odepa_catastro import fold

JOB={'id':'senamhi-arandano','source_ids':['pe-senamhi-agromet-arandano'],'schedule':'weekly',
     'description':'SENAMHI dekadal blueberry agrometeorological bulletins: PDF text, dekad dates and crop stage sentences',
     'max_bytes_per_run':300_000_000,'derived_only':False}
LISTING='https://www.senamhi.gob.pe/main.php?dp=la-libertad&p=boletines'
FILES='https://www.senamhi.gob.pe/load/file/'
PREFIX='02981SENA'
MONTHS={'enero':1,'febrero':2,'marzo':3,'abril':4,'mayo':5,'junio':6,'julio':7,'agosto':8,'septiembre':9,'setiembre':9,
        'octubre':10,'noviembre':11,'diciembre':12}
MES='('+'|'.join(MONTHS)+')'
# Bulletin stations and reference localities, then the regions and coastal zones the text names.
LOCALITIES=['Cayaltí','Chao','San José','Virú','Tacama','El Chira','Olmos','Motupe','Chepén','Trujillo','Chiclayo','Casma','Huarmey','Barranca','Cañete','Chincha','Pisco']
REGIONS=['Lambayeque','La Libertad','Piura','Tumbes','Áncash','Lima','Ica','Arequipa','Cajamarca','costa norte','costa central','costa sur']
STAGE_TERMS={'fases':r'\bfases?\b','floracion':r'\bfloracion\b','fructificacion':r'\bfructificacion\b',
             'maduracion':r'\bmaduracion\b','cosecha':r'\bcosechas?\b'}
# Cultivars grown on the Peruvian coast that the bulletins may name.
VARIETIES=['Ventura','Biloxi','Emerald','Sekoya Pop','Sekoya Beauty','Matías','Rocío','Atlas','Jupiter Blue','Mágica','Salvador',
           'Kirra','Arana','Bianca Blue','Raymi','Stellar','Abundance','Eureka']
HEADINGS=re.compile(r'(?P<forecast>pron[óo]stico\s+agrome\w+gico(?!\s*:))|(?P<stages>etapas\s+de\s+crecimiento)'
                    r'|(?P<impacts>impactos\s+del\s+clima(?:\s+en\s+el\s+cultivo(?:\s+de)?\s+ar[áa]ndano)?)|(?P<notes>tener\s+en\s+cuenta)',re.I)
DATE_LINES=re.compile(r'^(?:\d\s*°?\s*d[ée]cada\s+de\s+\w+\s+(?:de\s+)?\d{4}\s*(?:\([^)]*\)?)?|del\s+\d{1,2}\b.{0,40}?\d{4}'
                      r'|pr[óo]xima\s+actualizaci[óo]n\s*:?\s*\d{1,2}\s+de\s+\w+\s+(?:de\s+)?\d{4}|cultivo\s+de\s+ar[áa]ndano)\s*',re.I)

def listing_entries(html):
    """Blueberry bulletin links on the bulletins page: [{'id','prefix','seq','url','label'}], newest first."""
    out=[]
    for m in re.finditer(r'<a\s+href="([^"]*/load/file/((\d+SENA)-(\d+))\.pdf)"([^>]*)>([^<]*)<',html):
        url,bid,prefix,seq,attrs,label=m.groups()
        t=re.search(r'title="([^"]*)"',attrs)
        if t and 'arandano' in fold(t.group(1)):
            out.append({'id':bid,'prefix':prefix,'seq':int(seq),'url':url,'label':re.sub(r'\s+',' ',label).strip()})
    return out

def _date(d,mes,y):
    return pd.Timestamp(int(y),MONTHS[fold(mes)],int(d))

def bulletin_dates(text):
    """Forecast period, observed (monitored) dekad and next update date from the bulletin text."""
    out={'volume':None,'edition':None,'forecast_start':pd.NaT,'forecast_end':pd.NaT,'monitor_year':None,'monitor_month':None,
         'monitor_dekad':None,'monitor_start':pd.NaT,'monitor_end':pd.NaT,'next_update':pd.NaT}
    t=fold(text)
    if m:=re.search(r'\bvol\s+([ivxlc]+)\b',t): out['volume']=m.group(1).upper()
    if m:=re.search(r'\bedicion\s+([ivxlc]+)\b',t): out['edition']=m.group(1).upper()
    # 'Del 03 al 12 de octubre de 2026', 'Del 23 de diciembre 2025 al 01 de enero de 2026', 'Del 24 de julio 02 de agosto 2025'
    m=re.search(rf'\bdel\s+(\d{{1,2}})(?:\s+de\s+{MES})?(?:\s+(?:de\s+)?(\d{{4}}))?\s+(?:al\s+)?(\d{{1,2}})\s+de\s+{MES}\s+(?:de(?:l)?\s+)?(\d{{4}})',t)
    if m:
        d1,m1,y1,d2,m2,y2=m.groups()
        end=_date(d2,m2,y2)
        start=pd.Timestamp(int(y1 or y2),MONTHS[m1 or m2],int(d1))
        if start>end and not y1: start=start-pd.DateOffset(years=1)
        out['forecast_start'],out['forecast_end']=start,end
    if m:=re.search(rf'\b([123])\s*°?\s*decada\s+de\s+{MES}\s+(?:de(?:l)?\s+)?(\d{{4}})',t):
        k,mes,y=int(m.group(1)),MONTHS[m.group(2)],int(m.group(3))
        last=calendar.monthrange(y,mes)[1]
        out.update(monitor_year=y,monitor_month=mes,monitor_dekad=k,monitor_start=pd.Timestamp(y,mes,1+10*(k-1)),
                   monitor_end=pd.Timestamp(y,mes,last if k==3 else 10*k))
    if m:=re.search(rf'proxima\s+actualizacion\s*:?\s*(\d{{1,2}})\s+de\s+{MES}\s+(?:de(?:l)?\s+)?(\d{{4}})',t):
        out['next_update']=_date(*m.groups())
    return out

def _names(sentence,names):
    f=fold(sentence)
    return [n for n in names if re.search(r'\b'+re.escape(fold(n))+r'\b',f)]

def clean_text(t):
    t=re.sub(r'(\w)-\n(?=[a-záéíóúñ])',r'\1',t)  # rejoin words hyphenated across lines
    t=re.sub(r'([a-záéíóúñ\)])\d\b',r'\1',t)  # footnote markers such as 'Cayaltí1' or 'José)3'
    t=re.sub(r'[\u25cf\u2022\uf0b7\uf0a7\f]',' ',t)
    return re.sub(r'\s+',' ',t).strip()

def stage_sentences(text):
    """Sentences that mention crop stages, from reading-order text (pdftotext without -layout keeps columns apart).

    Justified columns come out with blank lines between words, so the text is joined first and cut at the
    bulletin's section headings; each sentence carries the section it sits in."""
    t=clean_text(text)
    cuts=[(m.start(),m.end(),m.lastgroup) for m in HEADINGS.finditer(t)]
    segments=[(None,t[:cuts[0][0]] if cuts else t)]+[(sec,t[e:cuts[i+1][0] if i+1<len(cuts) else len(t)]) for i,(s,e,sec) in enumerate(cuts)]
    rows=[]
    for section,seg in segments:
        seg=seg.strip()
        while (m:=DATE_LINES.match(seg)) and m.end(): seg=seg[m.end():]
        for s in re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡(])',seg):
            s=re.sub(r'^(?:\d\s+)+(?=[A-ZÁÉÍÓÚÑ])','',s)  # footnote numbers left in front of the map note
            f=fold(s)
            terms=[k for k,rx in STAGE_TERMS.items() if re.search(rx,f)]
            if not terms or len(s)<20: continue
            rows.append({'section':section,'sentence':s,'stage_terms':','.join(terms),'localities':','.join(_names(s,LOCALITIES)),
                         'regions':','.join(_names(s,REGIONS)),'varieties':','.join(_names(s,VARIETIES))})
    return rows

def pdftext(path,layout):
    cmd=['pdftotext','-enc','UTF-8']+(['-layout'] if layout else [])+[str(path),'-']
    return subprocess.run(cmd,capture_output=True,check=True,timeout=120).stdout.decode('utf-8','replace')

def _seq(name,prefix):
    m=re.fullmatch(re.escape(prefix)+r'-(\d+)\.pdf',name)
    return int(m.group(1)) if m else None

def plan(ctx):
    a=ctx.fetch(Request('listing',LISTING,filename='boletines_la_libertad.html',max_bytes=5_000_000))
    listed=listing_entries(a.path.read_text(encoding='utf-8',errors='replace')) if a.path else []
    prefix=listed[0]['prefix'] if listed else ctx.state.get('prefix',PREFIX)
    top=max([e['seq'] for e in listed]+[ctx.state.get('max_seq',0)])
    if not top: raise RuntimeError('bulletin listing unavailable and no earlier state to continue from')
    raw=ctx.paths.raw
    have={_seq(p.name,prefix) for p in raw.glob(f'{prefix}-*.pdf')} if raw.exists() else set()
    # Numbers above the newest listed one are probed when the listing could not be read.
    last=top if listed else top+2
    return [Request(f'pdf_{prefix}-{n}',f'{FILES}{prefix}-{n}.pdf',filename=f'{prefix}-{n}.pdf',max_bytes=30_000_000,optional=True)
            for n in range(1,last+1) if n not in have]

def _write_text(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.partial')
    tmp.write_text(text,encoding='utf-8'); os.replace(tmp,path)

def parse(ctx,assets):
    listing=assets.get('listing')
    listed=listing_entries(listing.path.read_text(encoding='utf-8',errors='replace')) if listing and listing.path else []
    prefix=listed[0]['prefix'] if listed else ctx.state.get('prefix',PREFIX)
    labels=dict(ctx.state.get('labels',{})); labels.update({e['id']:e['label'] for e in listed})
    pdfs=sorted(((_seq(p.name,prefix),p) for p in ctx.paths.raw.glob(f'{prefix}-*.pdf')),key=lambda x:x[0] or 0)
    bulletins,sentences,seen=[],[],{}
    for seq,path in pdfs:
        if seq is None: continue
        bid=f'{prefix}-{seq}'; data=path.read_bytes(); sha=hashlib.sha256(data).hexdigest()
        layout=pdftext(path,True)
        rel=f'text/{bid}.txt'; _write_text(ctx.paths.derived/rel,layout)
        meta=bulletin_dates(layout)
        bulletins.append({'bulletin_id':bid,'seq':seq,'url':f'{FILES}{bid}.pdf','sha256':sha,'bytes':len(data),
                          'pages':layout.count('\f') or None,**meta,'listing_label':labels.get(bid),'text_path':rel,
                          'chars':len(layout),'duplicate_of':seen.get(sha)})
        seen.setdefault(sha,bid)
        for i,s in enumerate(stage_sentences(pdftext(path,False))):
            sentences.append({'bulletin_id':bid,'seq':seq,'sentence_no':i,'monitor_start':meta['monitor_start'],'monitor_end':meta['monitor_end'],
                              'forecast_start':meta['forecast_start'],'forecast_end':meta['forecast_end'],**s})
    if not bulletins: raise RuntimeError('no bulletin PDFs stored')
    b=pd.DataFrame(bulletins).sort_values('seq').reset_index(drop=True)
    for c in ('monitor_year','monitor_month','monitor_dekad','pages'): b[c]=b[c].astype('Int64')
    s=pd.DataFrame(sentences)
    ctx.write_table('senamhi_bulletins',b)
    ctx.write_table('senamhi_stage_sentences',s)
    ctx.state.update(prefix=prefix,max_seq=int(b['seq'].max()),labels=labels)
    missing=sorted(k for k,a in assets.items() if k.startswith('pdf_') and a.status in ('missing','failed'))
    return {'bulletins':len(b),'stage_sentences':len(s),'undated':int(b['monitor_start'].isna().sum()),
            'duplicates':int(b['duplicate_of'].notna().sum()),'monitored_dekads':[str(b['monitor_start'].min().date()),str(b['monitor_end'].max().date())],
            'missing':missing}
