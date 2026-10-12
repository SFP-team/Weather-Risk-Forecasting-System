"""NOAA NCEI Storm Events details files (1996 onward), selected states and event types.

The directory listing is fetched first because each yearly file name carries a creation stamp
(`_cYYYYMMDD`) that changes when NCEI revises the year; the newest stamp per year is used.
Times are local standard time of the county or zone; CZ_TIMEZONE is 'CST' in old files and 'CST-6'
in newer ones, so the UTC offset is derived from either form.
"""
import re

import numpy as np
import pandas as pd

from ..runner import Request

LISTING = 'https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/'
FILE = re.compile(r'StormEvents_details-ftp_v1\.0_d(\d{4})_c(\d{8})\.csv\.gz')
FIRST_YEAR = 1996
JOB = {'id': 'storm-events', 'source_ids': ['noaa-storm-events'], 'schedule': 'monthly',
       'description': 'NOAA Storm Events details for blueberry states and crop-relevant event types (1996 onward)',
       'max_bytes_per_run': 1_000_000_000, 'derived_only': False}
STATES = {'FL': 'FLORIDA', 'GA': 'GEORGIA', 'SC': 'SOUTH CAROLINA', 'NC': 'NORTH CAROLINA', 'AL': 'ALABAMA',
          'MS': 'MISSISSIPPI', 'NJ': 'NEW JERSEY', 'MI': 'MICHIGAN', 'ME': 'MAINE', 'OR': 'OREGON',
          'WA': 'WASHINGTON', 'CA': 'CALIFORNIA'}
EVENT_TYPES = ['Frost/Freeze', 'Hail', 'Heavy Rain', 'Flash Flood', 'Excessive Heat', 'Heat', 'Tropical Storm',
               'Hurricane (Typhoon)', 'Hurricane', 'Extreme Cold/Wind Chill', 'Cold/Wind Chill']
ZONE_OFFSETS = {'AST': -4, 'EST': -5, 'EDT': -4, 'CST': -6, 'CDT': -5, 'MST': -7, 'MDT': -6, 'PST': -8, 'PDT': -7,
                'AKST': -9, 'AKDT': -8, 'HST': -10, 'SST': -11, 'GST': 10, 'CHST': 10}
DAMAGE_UNITS = {'': 1., 'H': 1e2, 'K': 1e3, 'M': 1e6, 'B': 1e9}
USECOLS = ['BEGIN_YEARMONTH', 'BEGIN_DAY', 'BEGIN_TIME', 'END_YEARMONTH', 'END_DAY', 'END_TIME', 'EPISODE_ID',
           'EVENT_ID', 'STATE', 'STATE_FIPS', 'YEAR', 'EVENT_TYPE', 'CZ_TYPE', 'CZ_FIPS', 'CZ_NAME', 'WFO',
           'CZ_TIMEZONE', 'DAMAGE_PROPERTY', 'DAMAGE_CROPS', 'MAGNITUDE', 'MAGNITUDE_TYPE', 'BEGIN_LAT', 'BEGIN_LON',
           'END_LAT', 'END_LON', 'EPISODE_NARRATIVE', 'EVENT_NARRATIVE']


def latest_files(listing_text):
    latest = {}
    for name, year, stamp in ((m.group(0), int(m.group(1)), m.group(2)) for m in FILE.finditer(listing_text)):
        if year not in latest or stamp > latest[year][1]:
            latest[year] = (name, stamp)
    return {year: name for year, (name, _) in latest.items()}


def damage(values):
    """'18.9M' -> 18.9e6, '0.00K' -> 0, '' -> NaN. Unknown suffixes give NaN, not zero."""
    parts = values.fillna('').str.strip().str.upper().str.extract(r'^(\d*\.?\d+)?\s*([A-Z]?)$')
    number = pd.to_numeric(parts[0], errors='coerce')
    scale = parts[1].map(DAMAGE_UNITS)
    return (number * scale).astype('float64')


def utc_offset(zones):
    parts = zones.fillna('').str.strip().str.upper().str.extract(r'^([A-Z]+)([+-]?\d+)?$')
    explicit = pd.to_numeric(parts[1], errors='coerce')
    return explicit.fillna(parts[0].map(ZONE_OFFSETS)).astype('float64')


def local_time(yearmonth, day, hhmm):
    text = yearmonth.str.strip() + day.str.strip().str.zfill(2) + hhmm.str.strip().str.zfill(4)
    return pd.to_datetime(text, format='%Y%m%d%H%M', errors='coerce')


def parse_file(path):
    raw = pd.read_csv(path, dtype=str, keep_default_na=False, usecols=USECOLS, compression='gzip')
    wanted = {name.upper() for name in EVENT_TYPES}
    raw = raw[raw.STATE.str.strip().str.upper().isin(STATES.values())
              & raw.EVENT_TYPE.str.strip().str.upper().isin(wanted)].reset_index(drop=True)
    abbr = {name: code for code, name in STATES.items()}
    frame = pd.DataFrame({
        'event_id': pd.to_numeric(raw.EVENT_ID, errors='coerce').astype('Int64'),
        'episode_id': pd.to_numeric(raw.EPISODE_ID, errors='coerce').astype('Int64'),
        'year': pd.to_numeric(raw.YEAR, errors='coerce').astype('Int64'),
        'state': raw.STATE.str.strip().str.upper().astype('string'),
        'state_abbr': raw.STATE.str.strip().str.upper().map(abbr).astype('string'),
        'state_fips': pd.to_numeric(raw.STATE_FIPS, errors='coerce').astype('Int64'),
        'cz_type': raw.CZ_TYPE.str.strip().astype('string'),
        'cz_fips': pd.to_numeric(raw.CZ_FIPS, errors='coerce').astype('Int64'),
        'cz_name': raw.CZ_NAME.str.strip().astype('string'),
        'wfo': raw.WFO.str.strip().astype('string'),
        'event_type': raw.EVENT_TYPE.str.strip().astype('string'),
        'begin_local': local_time(raw.BEGIN_YEARMONTH, raw.BEGIN_DAY, raw.BEGIN_TIME),
        'end_local': local_time(raw.END_YEARMONTH, raw.END_DAY, raw.END_TIME),
        'cz_timezone': raw.CZ_TIMEZONE.str.strip().astype('string'),
        'utc_offset_hours': utc_offset(raw.CZ_TIMEZONE),
        'damage_property_usd': damage(raw.DAMAGE_PROPERTY),
        'damage_crops_usd': damage(raw.DAMAGE_CROPS),
        'magnitude': pd.to_numeric(raw.MAGNITUDE, errors='coerce'),
        'magnitude_type': raw.MAGNITUDE_TYPE.str.strip().astype('string'),
        'begin_lat': pd.to_numeric(raw.BEGIN_LAT, errors='coerce'),
        'begin_lon': pd.to_numeric(raw.BEGIN_LON, errors='coerce'),
        'end_lat': pd.to_numeric(raw.END_LAT, errors='coerce'),
        'end_lon': pd.to_numeric(raw.END_LON, errors='coerce'),
        'episode_narrative': raw.EPISODE_NARRATIVE.astype('string'),
        'event_narrative': raw.EVENT_NARRATIVE.astype('string'),
    })
    # County FIPS only makes sense for county records; zone numbers are not FIPS counties.
    county = frame.cz_type.eq('C').fillna(False)
    frame['county_fips'] = (frame.state_fips.astype('string').str.zfill(2)
                            + frame.cz_fips.astype('string').str.zfill(3)).where(county).astype('string')
    shift = pd.to_timedelta(frame.utc_offset_hours, unit='h')
    frame['begin_utc'] = (frame.begin_local - shift).dt.tz_localize('UTC')
    frame['end_utc'] = (frame.end_local - shift).dt.tz_localize('UTC')
    text = raw.EPISODE_NARRATIVE + ' ' + raw.EVENT_NARRATIVE
    frame['mentions_blueberry'] = text.str.contains('blueberr', case=False, regex=False).to_numpy(dtype=bool)
    frame['source_file'] = path.name
    for column in ('begin_lat', 'begin_lon', 'end_lat', 'end_lon', 'magnitude'):
        frame[column] = frame[column].astype('float64').replace([np.inf, -np.inf], np.nan)
    return frame


def plan(ctx):
    listing = ctx.fetch(Request('listing', LISTING, filename='csvfiles_listing.html', max_bytes=5_000_000))
    if listing.path is None:
        raise RuntimeError(f'Storm Events listing unavailable ({listing.status})')
    files = latest_files(listing.path.read_text(errors='replace'))
    missing = [year for year in range(FIRST_YEAR, ctx.today.year) if year not in files]
    if missing:
        ctx.log('years_not_listed', years=missing)
    ctx.state['years_not_listed'] = missing
    return [Request(f'details_{year}', LISTING + files[year], max_bytes=200_000_000)
            for year in range(FIRST_YEAR, ctx.today.year + 1) if year in files]


def parse(ctx, assets):
    details = [asset for key, asset in sorted(assets.items()) if key.startswith('details_') and asset.path]
    if not details:
        raise ValueError('No Storm Events details files are available to parse')
    table = pd.concat([parse_file(asset.path) for asset in details], ignore_index=True)
    ctx.write_table('storm_events_selected', table)
    return {'rows': len(table), 'files': len(details), 'mentions_blueberry': int(table.mentions_blueberry.sum()),
            'crop_damage_usd': round(float(table.damage_crops_usd.sum()), 2)}
