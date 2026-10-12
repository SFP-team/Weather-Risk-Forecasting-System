"""USDA RMA Summary of Business by state, county, crop, coverage level, type, practice and unit
structure (sobtpu_<year>.zip), blueberry rows only.

Layout: SOBTPU_External_All_Years.pdf (27 pipe-separated fields). Checked against 1999 and 2022:
same 27 fields; 2022 ends lines with a bare CR, and coverage level is a percent (65.0000) in early
years but a fraction (.6500) later, so `coverage_level` is normalised to a fraction.
"""
import pandas as pd

from ..runner import Request
from .rma_col import pipe_rows, typed

BASE = 'https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/state_county_crop/'
FIRST_YEAR = 1999
JOB = {'id': 'rma-sobtpu', 'source_ids': ['us-rma-sob-state-county-crop'], 'schedule': 'monthly',
       'description': 'USDA RMA summary of business by type and practice, blueberry rows (1999 onward)',
       'max_bytes_per_run': 500_000_000, 'derived_only': False}
COLUMNS = ['commodity_year', 'state_code', 'state_name', 'state_abbr', 'county_code', 'county_name',
           'commodity_code', 'commodity_name', 'insurance_plan_code', 'insurance_plan_abbr', 'coverage_type_code',
           'coverage_level', 'delivery_id', 'type_code', 'type_name', 'practice_code', 'practice_name',
           'unit_structure_code', 'unit_structure_name', 'net_reporting_level_amount', 'reporting_level_type',
           'liability', 'total_premium', 'subsidy', 'indemnity', 'loss_ratio', 'endorsed_reporting_level_amount']
INTEGERS = ['commodity_year']
FLOATS = ['coverage_level', 'net_reporting_level_amount', 'liability', 'total_premium', 'subsidy', 'indemnity',
          'loss_ratio', 'endorsed_reporting_level_amount']


def parse_file(path):
    frame = typed(pipe_rows(path, COLUMNS, field=6), INTEGERS, FLOATS)
    frame['coverage_level'] = frame.coverage_level.where(frame.coverage_level <= 1, frame.coverage_level / 100)
    frame['fips'] = (frame.state_code.str.zfill(2) + frame.county_code.str.zfill(3)).astype('string')
    acres = frame.reporting_level_type.str.strip().str.lower() == 'acres'
    frame['insured_acres'] = frame.net_reporting_level_amount.where(acres.fillna(False))
    frame['source_file'] = path.name
    return frame


def plan(ctx):
    # RMA publishes the next crop year early (sobtpu_2027 existed in October 2026); those may 404.
    return [Request(f'sobtpu_{year}', f'{BASE}sobtpu_{year}.zip', max_bytes=100_000_000,
                    optional=year >= ctx.today.year) for year in range(FIRST_YEAR, ctx.today.year + 2)]


def parse(ctx, assets):
    frames = [parse_file(asset.path) for _, asset in sorted(assets.items()) if asset.path is not None]
    if not frames:
        raise ValueError('No sobtpu files are available to parse')
    table = pd.concat(frames, ignore_index=True)
    ctx.write_table('rma_sobtpu_blueberry', table)
    return {'rows': len(table), 'files': len(frames),
            'years': [int(table.commodity_year.min()), int(table.commodity_year.max())] if len(table) else None,
            'indemnity_usd': round(float(table.indemnity.sum()), 2)}

