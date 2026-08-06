from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[3]
for p in (
    ROOT,
    ROOT / "packages" / "common",
    ROOT / "packages" / "ingest",
    ROOT / "packages" / "features",
    ROOT / "packages" / "risk",
    ROOT / "packages" / "models",
    ROOT / "services" / "api",
):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from blueberry_common.config import get_settings  # noqa: E402
from blueberry_common.db import init_db  # noqa: E402
from app.routers import core  # noqa: E402

settings = get_settings()
init_db()

app = FastAPI(
    title="Florida Blueberry Weather Risk API",
    description=(
        "Decision-support API for Florida blueberry freeze, chill, and seasonal risk. "
        "Not a substitute for NWS warnings or UF/IFAS Extension advice."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(core.router)


@app.get("/")
def root():
    return {
        "name": "Florida Blueberry Weather Risk API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


def run() -> None:
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        app_dir=str(ROOT / "services" / "api"),
    )


if __name__ == "__main__":
    run()
