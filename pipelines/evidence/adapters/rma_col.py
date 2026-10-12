"""USDA RMA cause of loss with month of loss (colsom_<year>.zip), blueberry rows only.

Layout: COL_Summary_of_Business_with_Month_All_Years.pdf (30 pipe-separated fields). Checked against
real files for 1989 and 2022: same 30 fields; 1989 leaves plan abbreviation, cause description and
year of loss blank.
"""
import io
import zipfile

import pandas as pd

from ..runner import Request

BASE = 'https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/'
FIRST_YEAR = 1989
COMMODITY = '0012'  # blueberries
JOB = {'id': 'rma-col', 'source_ids': ['usda-rma-cause-of-loss'], 'schedule': 'monthly',
       'description': 'USDA RMA cause of loss by month of loss, blueberry rows (1989 onward)',
       'max_bytes_per_run': 500_000_000, 'derived_only': False}
COLUMNS = ['commodity_year', 'state_code', 'state_abbr', 'county_code', 'county_name', 'commodity_code',
           'commodity_name', 'insurance_plan_code', 'insurance_plan_abbr', 'coverage_category', 'stage_code',
           'cause_code', 'cause_description', 'month_of_loss', 'month_of_loss_name', 'year_of_loss',
           'policies_earning_premium', 'policies_indemnified', 'net_planted_quantity', 'net_endorsed_acres',
           'liability', 'total_premium', 'producer_paid_premium', 'subsidy', 'state_private_subsidy',
           'additional_subsidy', 'efa_premium_discount', 'net_determined_quantity', 'indemnity', 'loss_ratio']
INTEGERS = ['commodity_year', 'cause_code', 'month_of_loss', 'year_of_loss', 'policies_earning_premium',
            'policies_indemnified']
FLOATS = ['net_planted_quantity', 'net_endorsed_acres', 'liability', 'total_premium', 'producer_paid_premium',
          'subsidy', 'state_private_subsidy', 'additional_subsidy', 'efa_premium_discount',
          'net_determined_quantity', 'indemnity', 'loss_ratio']
# 46 (tropical storm), 47 (hurricane) and 64 (tornado) were found in the blueberry rows on 2026-10-12.
CAUSE_FAMILY = {42: 'freeze', 41: 'freeze', 43: 'cold', 44: 'cold', 31: 'excess_moisture', 21: 'hail',
                12: 'heat', 62: 'heat', 11: 'drought', 45: 'chill_shortfall', 81: 'disease',
                61: 'wind_storm', 92: 'wind_storm', 63: 'wind_storm', 46: 'wind_storm', 47: 'wind_storm', 64: 'wind_storm'}


def pipe_rows(path, columns, commodity=COMMODITY, field=5):
    """Rows of the single text member whose commodity field equals `commodity`.

    Text is read with universal newlines because some RMA files end lines with a bare CR."""
    with zipfile.ZipFile(path) as archive:
        members = [m for m in archive.namelist() if not m.endswith('/')]
        if len(members) != 1:
            raise ValueError(f'{path.name}: expected one member, found {members}')
        rows, first = [], True
        with io.TextIOWrapper(archive.open(members[0]), encoding='latin-1', newline=None) as text:
            for line in text:
                if first or f'|{commodity}|' in line:
                    parts = line.rstrip('\r\n').split('|')
                    if len(parts) != len(columns):
                        raise ValueError(f'{path.name}: expected {len(columns)} fields, found {len(parts)}')
                    if parts[field].strip() == commodity:
                        rows.append([p.strip() for p in parts])
                    first = False
    return pd.DataFrame(rows, columns=columns, dtype=object) if rows else pd.DataFrame(columns=columns, dtype=object)


def typed(frame, integers, floats):
    for column in integers:
        frame[column] = pd.to_numeric(frame[column], errors='coerce').astype('Int64')
    for column in floats:
        frame[column] = pd.to_numeric(frame[column], errors='coerce').astype('float64')
    for column in frame.columns.difference(integers + floats):
        frame[column] = frame[column].astype('string')
    return frame


def parse_file(path):
    frame = typed(pipe_rows(path, COLUMNS), INTEGERS, FLOATS)
    frame['fips'] = (frame.state_code.str.zfill(2) + frame.county_code.str.zfill(3)).astype('string')
    frame['cause_family'] = frame.cause_code.map(lambda c: CAUSE_FAMILY.get(int(c), 'other') if pd.notna(c)
                                                 else 'other').astype('string')
    frame['source_file'] = path.name
    return frame


def plan(ctx):
    # The current year's file may not exist early in the year, so only that one is optional.
    return [Request(f'colsom_{year}', f'{BASE}colsom_{year}.zip', max_bytes=100_000_000,
                    optional=year >= ctx.today.year) for year in range(FIRST_YEAR, ctx.today.year + 1)]


def parse(ctx, assets):
    frames = [parse_file(asset.path) for _, asset in sorted(assets.items()) if asset.path is not None]
    if not frames:
        raise ValueError('No colsom files are available to parse')
    table = pd.concat(frames, ignore_index=True)
    ctx.write_table('rma_col_blueberry', table)
    return {'rows': len(table), 'files': len(frames),
            'years': [int(table.commodity_year.min()), int(table.commodity_year.max())] if len(table) else None,
            'indemnity_usd': round(float(table.indemnity.sum()), 2)}
