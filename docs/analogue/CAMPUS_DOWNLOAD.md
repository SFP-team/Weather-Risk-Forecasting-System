# Campus download bot

The Cursor cloud agent **cannot** see your university server or Eduroam. Nothing started from this chat will use that Wi-Fi. You start the job **on that machine**, leave it in `tmux`, and it uses campus bandwidth.

## Can you set it up today?

**Yes, on the university box.** Copy this repo there, start the bot, walk away.

**No, not from here.** I have no SSH path to that server.

## Will terabytes finish in two or three days on Eduroam Wi-Fi?

**Usually no**, if “everything” means a global ERA5-Land hourly cube (5–20 TB).

| Pack | Size | Eduroam Wi-Fi in 2–3 days? |
|---|---|---|
| `tonight` — 303 catalog POWER daily | ~70 MB | Yes, an hour |
| `future` — catalog + 1° land + blueberry belts, POWER daily | ~3–8 GB | Yes, overnight to a day |
| Global 0.25° daily 10y | ~30 GB | Maybe, if Wi-Fi stays up |
| ERA5-Land hourly **global** 10y | 5–20 TB | No. CDS queues + Wi-Fi. Need wired + weeks |

Sustained Eduroam is often 20–80 Mbps shared. That is about **0.6–2.5 TB/day** in a perfect world. Real Wi-Fi drops, sleeps, and rate limits. A box on **wired campus Ethernet** is the right host. A laptop that leaves the building is not.

`future` is the pack this product needs for the next year: dated T / rain / solar at every point we will diagnose or sample. Formulas derive chill and harvest rain. You do not need the 20 TB cube to start.

## Run it on the university server

```bash
# once, on THAT machine (not this cloud VM)
git clone <this-repo> && cd Weather-Risk-Forecasting-System
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# see the plan without downloading
python3 -m blueberry_analogue.cli download --plan future --dry-run

# start and leave it (tmux survives SSH disconnect)
tmux new -s weather
python3 -m blueberry_analogue.cli download --plan future --workers 4
# detach: Ctrl-b then d
# reattach later: tmux attach -t weather
```

Resume is automatic. Re-run the same command; finished points are skipped. Progress: `data/analogue/weather/download_progress.json`. Data: `data/analogue/weather/daily.sqlite`.

Before you start:

1. `df -h` — keep at least 20 GB free for `future`.
2. Disable sleep / idle Wi-Fi power save on that host.
3. Prefer a wired jack over Eduroam if IT will give you one.
4. Check the campus acceptable-use policy. Research bulk download of NASA POWER is normally fine; a 20 TB scrape may need a word with IT.
5. NASA POWER needs no account. ERA5 / AgERA5 need a Copernicus CDS API key — the bot only **writes** request JSON under `data/analogue/weather/cds_jobs/`. It does not pull ERA5 until you add that key and run CDS yourself.

## What this is not

It is not a bot I can trigger from Cursor onto Eduroam. It is not a global hourly cube. It is a resume-safe POWER daily harvester you start on campus so the download never touches your personal phone plan.
