"""Audit completed soil pilot artifacts without starting downloads."""
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from discover import ROOT, write_json
from soil_pilot import sample


def run():
    state=json.loads((ROOT/'state/soil_pilot.json').read_text())
    issues=[]; counts=Counter(); groups=defaultdict(dict); grids=defaultdict(set); nodata=0
    for key,job in state['jobs'].items():
        if job['status'] not in ('valid','source_nodata'):continue
        path=ROOT/job['raw_path']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=job['sha256']:
            issues.append({'job':key,'issue':'checksum'})
        reread=sample(path,job,job['property'])
        if reread['value']!=job['value']:issues.append({'job':key,'issue':'readback'})
        counts[job['site_name']]+=1
        nodata+=int(job['value'] is None)
        groups[(job['site_id'],job['property'],job['depth'])][job['statistic']]=job['value']
        grids[(job['site_id'],job['property'],job['depth'])].add(
            (job['crs'],job['cell_lon'],job['cell_lat'],*job['resolution']))
    paired=0
    for key,values in groups.items():
        if len(grids[key])!=1:issues.append({'group':list(key),'issue':'unaligned_statistic_grids'})
        low,high=values.get('Q0.05'),values.get('Q0.95')
        if low is not None and high is not None:
            paired+=1
            if low>high:issues.append({'group':list(key),'issue':'reversed_quantiles'})
    report={'generated':datetime.now(timezone.utc).isoformat(),'worker_status':state['status'],
        'expected_jobs':state['total_jobs'],'audited_jobs':sum(counts.values()),
        'site_records':dict(counts),'source_nodata_records':nodata,
        'quantile_pairs_checked':paired,'issues':issues,
        'scope':'Checksums, raster readback and quantile order; not field validation.',
        'grid_note':'Live WCS outputs EPSG:4326 geographic subsets (~0.0025 degrees here). Stored cell coordinates are returned-grid centers, not native SoilGrids centers.'}
    write_json(ROOT/'reports/soil_audit.json',report)
    print(json.dumps(report))
    if issues:raise RuntimeError('Soil audit issues')


if __name__=='__main__':run()
