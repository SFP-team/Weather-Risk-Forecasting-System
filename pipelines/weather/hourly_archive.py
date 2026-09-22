"""Point extraction from the existing, checksummed hourly cache. Never downloads."""
import hashlib
import json
import math
import sqlite3
from pathlib import Path

import numpy as np

from pilot import Source


class ArchiveReader:
    """Downloads.get-compatible reader without acquisition or database writes."""
    def __init__(self, root):
        self.root = Path(root)
        self.db = sqlite3.connect((self.root / 'state/jobs.sqlite').resolve().as_uri() + '?mode=ro', uri=True)
        self.hashes = {}

    def get(self, url, path, api=False):
        row = self.db.execute('SELECT status,sha256 FROM objects WHERE url=?', (url,)).fetchone()
        # KeyError would let Zarr silently substitute fill values for a missing chunk.
        if not row or row[0] != 'downloaded' or not path.is_file():
            raise RuntimeError('Required hourly archive object is unavailable; no download attempted')
        data = path.read_bytes()
        checksum = hashlib.sha256(data).hexdigest()
        if checksum != row[1]:
            raise RuntimeError('Hourly archive checksum mismatch; refusing analysis')
        self.hashes[url] = checksum
        return data


def hourly_from_cache(root, lat, lon):
    """Return complete 2010–2025 UTC temperature and public source provenance."""
    root = Path(root)
    if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError('Invalid coordinate')
    if not (root / 'data/raw/zarr/met_hourly').exists():
        return None, None
    reader = ArchiveReader(root)
    try:
        source = Source(reader, 'met_hourly')
        frame, metadata = source.point({'lat': lat, 'lon': lon}, '2010-01-01', '2025-12-31')
        if len(frame) != 140256 or not np.isfinite(frame[['tmean_c', 'dewpoint_mean_c']].to_numpy()).all():
            raise RuntimeError('Hourly archive series is incomplete; refusing crop analysis')
        series = frame.set_index('time').tmean_c
        sy, sx = metadata['source_lat'], metadata['source_lon']
        a = math.sin(math.radians(sy-lat)/2)**2 + math.cos(math.radians(lat))*math.cos(math.radians(sy))*math.sin(math.radians(sx-lon)/2)**2
        identity = {'objects': reader.hashes, 'source_indices': metadata['source_indices'],
                    'start': '2010-01-01', 'end': '2025-12-31', 'schema': 'cached-hourly-point-v1'}
        provenance = {'sha256': hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest(),
                      'site': 'Global hourly archive', 'source_lat': sy, 'source_lon': sx,
                      'source_indices': metadata['source_indices'], 'cell_degrees': [0.5, 0.625],
                      'distance_km': round(2*6371.0088*math.asin(math.sqrt(min(1., a))), 1),
                      'rows': len(series), 'start': '2010-01-01', 'end': '2025-12-31',
                      'time_standard': 'UTC', 'source_version': metadata['source_version'],
                      'source_url': metadata['source_url'],
                      'note': 'Existing land-hourly archive; one native grid series per cell, not a field measurement.'}
        return series, provenance
    except (KeyError, ValueError) as exc:
        raise RuntimeError('Invalid hourly archive metadata or series; refusing analysis') from exc
    finally:
        reader.db.close()
