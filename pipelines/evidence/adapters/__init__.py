"""Job id to adapter module. Modules are imported only when a job is used, so one broken or
missing adapter does not stop the others or the CLI."""
import importlib

MODULES = {
    'rma-col': 'rma_col',
    'rma-sobtpu': 'rma_sobtpu',
    'storm-events': 'storm_events',
    'ghcnh-stations': 'ghcnh_stations',
    'station-truth': 'station_truth',
    'odepa-catastro': 'odepa_catastro',
    'odepa-exports': 'odepa_exports',
    'comext-blueberry': 'comext_blueberry',
    'senamhi-arandano': 'senamhi_arandano',
}


def load(job_id):
    if job_id not in MODULES:
        raise KeyError(f'Unknown evidence job {job_id!r}; known: {", ".join(MODULES)}')
    module = importlib.import_module(f'{__name__}.{MODULES[job_id]}')
    if module.JOB['id'] != job_id:
        raise ValueError(f'{MODULES[job_id]}.JOB id is {module.JOB["id"]!r}, expected {job_id!r}')
    return module
