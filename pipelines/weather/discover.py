"""Inspect public source metadata on the server; never fetch global arrays."""
import json
import os
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path('/media/fpt/fpt2/Weather_Claude')
BASE = 'https://nasa-power.s3.us-west-2.amazonaws.com/'
STORES = {
    'met_daily': 'merra2/temporal/power_merra2_daily_temporal_utc.zarr',
    'solar_daily': 'syn1deg/temporal/power_syn1deg_daily_temporal_utc.zarr',
    'met_hourly': 'merra2/temporal/power_merra2_hourly_temporal_utc.zarr',
}
PARAMETERS = ['T2M_MIN', 'T2M_MAX', 'T2M', 'PRECTOTCORR', 'RH2M',
              'ALLSKY_SFC_SW_DWN', 'WS2M', 'T2MDEW']


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.partial')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False))
    os.replace(tmp, path)


def main():
    mount = subprocess.check_output(['findmnt', '-n', '-o', 'TARGET', '-T', str(ROOT)], text=True).strip()
    if mount != '/media/fpt/fpt2':
        raise RuntimeError('Project drive is not mounted at its verified location')
    preflight = {'mount': mount, 'cds_config_present': Path('/home/fpt/.cdsapirc').is_file()}
    write_json(ROOT / 'reports/preflight.json', preflight)
    print(json.dumps(preflight), flush=True)
    for name, prefix in STORES.items():
        url = BASE + prefix + '/.zmetadata'
        with urllib.request.urlopen(url, timeout=60) as r:
            payload = r.read(10 * 1024 * 1024 + 1)
        if len(payload) > 10 * 1024 * 1024:
            raise RuntimeError('Metadata exceeded safety bound')
        metadata = json.loads(payload)
        write_json(ROOT / f'state/sources/{name}.json', metadata)
        entries = metadata['metadata']
        variables = sorted(k[:-8] for k in entries if k.endswith('/.zarray'))
        summary = {'source': name, 'url': BASE + prefix, 'global_attrs': entries.get('.zattrs'),
                   'variables': variables, 'selected': {}}
        for parameter in PARAMETERS + ['time', 'lat', 'lon']:
            if parameter + '/.zarray' in entries:
                summary['selected'][parameter] = {
                    'array': entries[parameter + '/.zarray'],
                    'attrs': entries.get(parameter + '/.zattrs', {})}
        write_json(ROOT / f'reports/source_{name}.json', summary)
        print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
