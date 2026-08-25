# Blueberry Analogue

Shortlist the next trial geography for a blueberry variety and production system. This is not the Florida tonight-freeze product in `apps/web`.

**Job.** You already have a farm that works, or a variety × system card. The tool returns places worth visiting, what will go wrong there, how much the weather data can be trusted, and a checklist that starts at book the flight.

**It does not say plant 20 ha.** Similarity is not identity.

## What is in this tree

| Piece | Where |
|---|---|
| Five class cards + cultivars | `packages/analogue/blueberry_analogue/data/variety_cards.yaml` |
| 200+ geocoded operations | `packages/analogue/blueberry_analogue/data/site_catalog.py` |
| NASA POWER / CHELSA / CHIRPS / ERA5-Land / SoilGrids / DEM | `packages/analogue/blueberry_analogue/climate/fetch.py` |
| Dual chill + stage features | `packages/analogue/blueberry_analogue/features/` |
| CCAFS lag + Hallegatte gates | `packages/analogue/blueberry_analogue/analogue/engine.py` |
| Skill sheet | [skill-sheet.md](skill-sheet.md) |
| Map UI | `apps/analogue-web/` on port 8010 |

## Run it

```bash
pip install -e .
python -m blueberry_analogue.cli sites
python -m blueberry_analogue.cli build          # offline fallback climate
python -m blueberry_analogue.cli build --live   # NASA POWER + SoilGrids + DEM points
python -m blueberry_analogue.cli serve          # http://127.0.0.1:8010
```

`--live` pulls **point** climatologies. It does not download a global hourly cube. Stage CHELSA and CHIRPS GeoTIFFs under `data/analogue/chelsa` and `data/analogue/chirps` when you want the 1 km screen.

## Honest claims

After leave-one-region-out skill on chill or freeze beats Baseline-0, we may say more transferable than climate distance.

If we only have presence AUC inside the training continent, we may say the model describes where blueberries are grown in this dataset.

We may not say this site will grow like Michigan. We may not quote Wang & Dong 0.94.
