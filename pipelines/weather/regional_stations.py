"""Bounded regional observation pilot; raw station archives remain untouched."""
import argparse
import io
import json
import zipfile
import numpy as np
import pandas as pd
import zarr
from pilot import nearest_indices
from validate_observations import fetch
from postprocess import ROOT, km_distance
from discover import write_json


def compare_daily(daily, lat, lon):
    group=zarr.open_consolidated(str(ROOT/'data/normalized/global/met_daily'),mode='r')
    y,x=nearest_indices(group['lat'][:],group['lon'][:],lat,lon)
    grid=pd.DataFrame({v:group[v][:,y,x] for v in daily.columns},index=pd.date_range('2010-01-01','2025-12-31',tz='UTC'))
    result={'grid_lat':float(group['lat'][y]),'grid_lon':float(group['lon'][x]),
            'grid_distance_km':km_distance(lat,lon,float(group['lat'][y]),float(group['lon'][x])), 'metrics':{}}
    for var in daily:
        pairs=pd.concat({'observed':daily[var],'grid':grid[var].reindex(daily.index)},axis=1).dropna()
        error=pairs.grid-pairs.observed
        metrics={'days':len(pairs),'bias':float(error.mean()) if len(pairs) else None,
                 'mae':float(error.abs().mean()) if len(pairs) else None,
                 'rmse':float(np.sqrt((error**2).mean())) if len(pairs) else None}
        if var=='tmin_c':
            metrics['below_zero']={'observed':int((pairs.observed<0).sum()),'grid':int((pairs.grid<0).sum()),
                'hits':int(((pairs.observed<0)&(pairs.grid<0)).sum()),
                'misses':int(((pairs.observed<0)&(pairs.grid>=0)).sum()),
                'false_alarms':int(((pairs.observed>=0)&(pairs.grid<0)).sum())}
        metrics['monthly']={str(month):{'days':len(block),'bias':float(block.mean()),'mae':float(block.abs().mean())}
                            for month,block in error.groupby(error.index.month)}
        result['metrics'][var]=metrics
    return result


def fawn():
    path=ROOT/'data/reference/validation/fawn_2020.zip'
    columns=['ID','UTC','temp_air_2m_C','quality_flag_temp_air_2m_C','rain_2m_inches','quality_flag_rain_2m_inches']
    selected=[]
    with zipfile.ZipFile(path) as archive:
        with archive.open('2020.csv') as stream:
            for chunk in pd.read_csv(stream,usecols=columns,dtype=str,chunksize=100000):
                selected.append(chunk[chunk.ID=='250'])
    raw=pd.concat(selected,ignore_index=True)
    raw['time']=pd.to_datetime(raw.UTC,utc=True)
    if raw.time.duplicated().any():
        raise ValueError('Duplicate Citra timestamps; requires adjudication')
    if (raw.time.dt.minute%15!=0).any() or (raw.time.dt.second!=0).any():
        raise ValueError('Unexpected Citra timestamp cadence')
    out=ROOT/'data/normalized/stations/FAWN_250_2020.parquet'
    raw.to_parquet(out,index=False)
    # CSV serializes integer flag codes as decimals (e.g. "0.0", "17.0").
    # Preserve original strings; canonicalize only integral suffixes for filtering.
    flags=raw.quality_flag_temp_air_2m_C.str.replace(r'\.0+$','',regex=True)
    series=pd.to_numeric(raw.temp_air_2m_C,errors='coerce').where(flags=='0')
    series.index=pd.DatetimeIndex(raw.time)
    series=series.sort_index().reindex(pd.date_range('2020-01-01','2021-01-01',freq='15min',inclusive='left',tz='UTC'))
    counts=series.resample('D').count()
    daily=pd.DataFrame({'tmin_c':series.resample('D').min(),'tmax_c':series.resample('D').max()}).where(counts.eq(96),axis=0)
    daily.to_parquet(out.with_name('FAWN_250_2020_daily.parquet'))
    result={'station':'FAWN Citra 250','latitude':29.4101,'longitude':-82.1732,'year':2020,
        'raw_records':len(raw),'complete_temperature_days':int(counts.eq(96).sum()),
        'quality_flag_counts':raw.quality_flag_temp_air_2m_C.value_counts(dropna=False).to_dict(),
        'comparison':compare_daily(daily,29.4101,-82.1732),
        'limitations':['Only 2020; not a multi-year validation.',
        '96 accepted 15-minute temperature samples required per UTC day; no filling.',
        'Sampled temperature extrema can miss between-sample extremes.',
        'Rainfall comparison withheld: metadata labels inches/hour; interval accumulation semantics need independent confirmation.',
        'No bias correction fitted; quality filters can exclude genuine extremes as well as errors.']}
    write_json(ROOT/'reports/fawn_citra_2020.json',result)
    print(json.dumps(result),flush=True)


def inmet():
    candidates=json.loads((ROOT/'reports/inmet_candidates.json').read_text())['candidates'][:2]
    results=[]
    with zipfile.ZipFile(ROOT/'data/reference/validation/inmet_2020.zip') as archive:
        for site in candidates:
            with archive.open(site['file']) as stream:
                raw=pd.read_csv(stream,skiprows=8,sep=';',decimal=',',encoding='latin1')
            raw['time']=pd.to_datetime(raw['Data']+' '+raw['Hora UTC'].str.replace(' UTC','',regex=False),format='%Y/%m/%d %H%M',utc=True)
            if raw.time.duplicated().any():
                raise ValueError('Duplicate INMET timestamps')
            code=site['file'].split('_')[3]
            path=ROOT/'data/normalized/stations'/f'INMET_{code}_2020.parquet'
            raw.to_parquet(path,index=False)
            variables={'tmin_c':'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
                       'tmax_c':'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
                       'precip_mm':'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'}
            hourly=pd.DataFrame({name:pd.to_numeric(raw[column],errors='coerce').to_numpy() for name,column in variables.items()},index=pd.DatetimeIndex(raw.time))
            # Sentinel and coarse numeric screening, not provider-certified quality control.
            bad=(hourly[['tmin_c','tmax_c']] < -90)|(hourly[['tmin_c','tmax_c']] > 60)
            hourly[['tmin_c','tmax_c']]=hourly[['tmin_c','tmax_c']].mask(bad)
            hourly.precip_mm=hourly.precip_mm.where(hourly.precip_mm>=0)
            reversed_temp=hourly.tmin_c>hourly.tmax_c
            hourly.loc[reversed_temp,['tmin_c','tmax_c']]=np.nan
            hourly=hourly.sort_index().reindex(pd.date_range('2020-01-01','2021-01-01',freq='h',inclusive='left',tz='UTC'))
            # INMET extrema refer to the preceding hour. Move an interval ending at
            # midnight into the previous day. Last day is incomplete without next year's 00 UTC.
            shifted=hourly.copy()
            shifted.index=shifted.index-pd.Timedelta(nanoseconds=1)
            counts=shifted.resample('D').count()
            daily=shifted.resample('D').agg({'tmin_c':'min','tmax_c':'max','precip_mm':'sum'}).where(counts==24)
            daily=daily.loc['2020-01-01':'2020-12-31']
            daily.to_parquet(path.with_name(f'INMET_{code}_2020_daily.parquet'))
            results.append({'station':code,'metadata':site,'hourly_records':len(raw),
                'complete_days':daily.notna().sum().to_dict(),'temperature_order_failures':int(reversed_temp.sum()),
                'comparison':compare_daily(daily,site['lat'],site['lon'])})
    report={'year':2020,'results':results,'limitations':[
        '2020 pilot only; no bias correction or agronomic validation.',
        'Source CSV has no per-measurement QC flags; only sentinels, broad bounds and temperature order screened.',
        'Previous-hour temperature extrema aggregated over 24 complete hourly intervals per UTC day.',
        'Hourly rainfall is provisionally treated as interval-ending accumulation; confirm provider convention before interpreting daily rainfall errors.',
        'No filled observations; incomplete days excluded per variable. Rainfall has not received comprehensive outlier screening.',
        'Nearby stations do not measure the Papanduva field; terrain and elevation differences remain.']}
    write_json(ROOT/'reports/inmet_near_papanduva_2020.json',report)
    print(json.dumps(report),flush=True)


def acquire():
    fetch(ROOT,'fawn_metadata.txt','https://fawn.ifas.ufl.edu/data/fawn_data_qaqc_pub/metadata.txt')
    for name,url,limit in [
        ('fawn_2020.zip','https://fawn.ifas.ufl.edu/data/fawn_data_qaqc_pub/2020.csv.zip',120*1024**2),
        ('inmet_2020.zip','https://portal.inmet.gov.br/uploads/dadoshistoricos/2020.zip',400*1024**2)]:
        data=fetch(ROOT,name,url,limit)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            files=[f for f in archive.infolist() if f.filename.lower().endswith('.csv') and not f.filename.startswith('__MACOSX/')]
            if len(files)>1500 or sum(f.file_size for f in files)>4*1024**3:
                raise ValueError('Archive exceeds inspection limits')
            if name.startswith('fawn'):
                for file in files[:2]:
                    with archive.open(file) as stream:
                        print(file.filename,stream.readline().decode()[:12000],flush=True)
            else:
                candidates=[]
                for file in files:
                    with archive.open(file) as stream:
                        header=[stream.readline().decode('latin1').strip() for _ in range(9)]
                    metadata={line.split(';')[0].strip(':\ufeff'):line.split(';')[1] for line in header[:8] if ';' in line}
                    try:
                        lat=float(metadata['LATITUDE:'].replace(',','.')) if 'LATITUDE:' in metadata else float(metadata['LATITUDE'].replace(',','.'))
                        lon=float(metadata.get('LONGITUDE:',metadata.get('LONGITUDE')).replace(',','.'))
                    except (KeyError,ValueError,TypeError):
                        continue
                    distance=km_distance(-26.312389,-50.080639,lat,lon)
                    if distance<=150:
                        candidates.append({'file':file.filename,'distance_km':distance,'header':header,'lat':lat,'lon':lon})
                candidates.sort(key=lambda x:x['distance_km'])
                write_json(ROOT/'reports/inmet_candidates.json',{'year':2020,'candidates':candidates})
                print(json.dumps(candidates),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['acquire','fawn','inmet'],default='acquire',nargs='?')
    globals()[parser.parse_args().action]()
