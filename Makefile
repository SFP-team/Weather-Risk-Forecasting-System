.PHONY: setup pipeline api web test analogue analogue-serve

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	cd apps/web && npm install

pipeline:
	. .venv/bin/activate && python pipelines/run_all.py

api:
	. .venv/bin/activate && cd services/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web:
	cd apps/web && npm run dev

test:
	. .venv/bin/activate && pytest -q

analogue:
	. .venv/bin/activate && python -m blueberry_analogue.cli build

analogue-serve:
	. .venv/bin/activate && python -m blueberry_analogue.cli serve
