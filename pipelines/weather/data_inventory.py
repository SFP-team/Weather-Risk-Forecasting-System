"""Read-only data tree inventory; does not merge incompatible spatial/time grids."""
import json
from importlib.metadata import version
from datetime import datetime, timezone
from discover import ROOT, write_json


def build():
    groups={}
    # Discover every raw/normalized family, including station archives.
    names = {str(p.relative_to(ROOT/'data')) for parent in ('raw','normalized')
             if (ROOT/'data'/parent).exists()
             for p in (ROOT/'data'/parent).iterdir() if p.is_dir()}
    names.update(('derived','reference'))
    for name in sorted(names):
        path=ROOT/'data'/name
        files=[p for p in path.rglob('*') if p.is_file()] if path.exists() else []
        groups[name]={'exists':path.exists(),'files':len(files),
                      'file_bytes':sum(p.stat().st_size for p in files),
                      'path':str(path.relative_to(ROOT))}
    states={}
    for name in ('global','soil_pilot'):
        p=ROOT/'state'/f'{name}.json'
        data=json.loads(p.read_text()) if p.exists() else {}
        states[name]={k:data[k] for k in ('status','updated','total_tiles','completed_tiles',
            'total_jobs','completed_jobs','response_bytes') if k in data}
    report={'generated':datetime.now(timezone.utc).isoformat(),'groups':groups,'states':states,
        'soil_runtime':{p:version(p) for p in ('rasterio','affine','numpy','requests')},
        'notes':['Snapshot while soil worker may be running; not a full checksum/scientific audit.',
            'Logical file bytes are not disk allocation or network transfer.',
            'Global weather 2010–2025; analysis baseline 2011–2025. Native met/solar grids remain separate.',
            'Soil is static prediction at three depths, not weather-aligned annual soil observations.',
            'Original files preserved. Inventory is a catalog, not duplicated or flattened data.']}
    write_json(ROOT/'reports/data_inventory.json',report)
    print(json.dumps(report))


if __name__=='__main__':build()
