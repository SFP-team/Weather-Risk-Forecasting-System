"""Resume-safe campus downloader for NASA POWER daily.

Run this on the university machine (Eduroam / campus Ethernet), not from
the Cursor cloud VM. The cloud agent cannot see that Wi-Fi.

This is not an ERA5 global hourly cube. It pulls dated daily T / rain /
solar at the points we will query. That is the 'everything we need' pack
for the next year of diagnose + recommend-where.
"""

from __future__ import annotations

import json
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from blueberry_analogue.climate.fetch import era5land_request_payload, agera5_request_payload
from blueberry_analogue.paths import CDS_JOBS, WEATHER_PROGRESS, ensure_data_dirs
from blueberry_analogue.weather.daily import fetch_nasa_power_daily
from blueberry_analogue.weather.grid import GridPoint, plan_estimate, plan_points
from blueberry_analogue.weather.store import WeatherStore, weather_store


def _write_progress(payload: dict[str, Any]) -> None:
    ensure_data_dirs()
    WEATHER_PROGRESS.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _free_gb(path: Path) -> float:
    usage = shutil.disk_usage(path)
    return usage.free / (1024**3)


def write_cds_job_stubs() -> list[Path]:
    """JSON you can hand to cdsapi later. Does not download ERA5."""
    ensure_data_dirs()
    CDS_JOBS.mkdir(parents=True, exist_ok=True)
    belts = {
        "se_us": [(26.0, -82.0), (36.0, -76.0)],
        "chile": [(-36.0, -72.0), (-33.0, -70.5)],
        "brazil_south": [(-29.0, -51.0), (-23.0, -47.0)],
        "iberia": [(37.2, -7.0), (42.0, -2.0)],
    }
    written: list[Path] = []
    for name, pts in belts.items():
        era = era5land_request_payload(pts)
        age = agera5_request_payload(pts)
        path = CDS_JOBS / f"{name}.json"
        path.write_text(json.dumps({"era5land": era, "agera5": age}, indent=2), encoding="utf-8")
        written.append(path)
    return written


def _fetch_one(point: GridPoint) -> tuple[GridPoint, Any]:
    frame = fetch_nasa_power_daily(point.lat, point.lon)
    return point, frame


def run_campus_download(
    plan: str = "tonight",
    *,
    live: bool = True,
    workers: int = 4,
    store: WeatherStore | None = None,
    dry_run: bool = False,
    sleep_s: float = 0.15,
    min_free_gb: float = 5.0,
) -> dict[str, Any]:
    if not live and not dry_run:
        raise ValueError("Campus download is a live POWER job. Use --dry-run to inspect the plan.")
    db = store or weather_store()
    points = plan_points(plan)
    estimate = plan_estimate(plan)
    done = db.complete_ids()
    pending = [p for p in points if p.point_id not in done]
    free = _free_gb(db.path.parent)
    report: dict[str, Any] = {
        "plan": plan,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "points_total": len(points),
        "points_done": len(points) - len(pending),
        "points_pending": len(pending),
        "estimate": estimate,
        "free_gb": round(free, 1),
        "db": str(db.path),
        "ok": 0,
        "fail": 0,
    }
    print(
        f"plan={plan} total={len(points)} done={report['points_done']} "
        f"pending={len(pending)} ~{estimate['disk_mb']} MB ~{estimate['hours_at_4_workers']} h "
        f"free={free:.1f} GB"
    )
    if dry_run:
        write_cds_job_stubs()
        report["cds_jobs"] = str(CDS_JOBS)
        _write_progress(report)
        return report
    if free < min_free_gb:
        raise RuntimeError(f"Only {free:.1f} GB free. Need about {min_free_gb:.0f} GB before starting.")

    _write_progress(report)
    if not pending:
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        _write_progress(report)
        return report

    workers = max(1, min(workers, 8))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_fetch_one, point) for point in pending]
        for i, fut in enumerate(as_completed(futs), start=1):
            point, frame = fut.result()
            if frame is not None and len(frame) > 200:
                db.put_series(
                    point.point_id,
                    point.lat,
                    point.lon,
                    frame,
                    "nasa_power_daily",
                    name=point.name,
                    kind=point.kind,
                )
                report["ok"] += 1
                print(f"ok   {point.point_id:28} {point.kind:12} {len(frame)} days")
            else:
                report["fail"] += 1
                print(f"fail {point.point_id:28} {point.kind:12}")
            report["points_done"] = int(estimate["points"]) - (len(pending) - report["ok"] - report["fail"])
            if i % 10 == 0 or i == len(pending):
                report["updated_at"] = datetime.now(timezone.utc).isoformat()
                _write_progress(report)
            if sleep_s:
                time.sleep(sleep_s)

    write_cds_job_stubs()
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["cds_jobs"] = str(CDS_JOBS)
    _write_progress(report)
    print(f"done ok={report['ok']} fail={report['fail']} db={db.path}")
    return report
