.PHONY: setup lint test evidence replay serve-evidence clean

setup:
	pip install -r requirements-dev.txt

lint:
	ruff check backend/rca_evidence backend/evidence_app.py scripts tests --select E,W,F --ignore E501

test:
	pytest -q

evidence:
	python scripts/validate_evidence.py
	python -m pip_audit -r backend/requirements-evidence.txt --progress-spinner off
	python -m bandit -r backend/rca_evidence backend/evidence_app.py -q

replay:
	python scripts/run_evidence_benchmark.py --stage replay

serve-evidence:
	uvicorn evidence_app:app --app-dir backend --host 127.0.0.1 --port 8088

clean:
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null; find . -name '*.pyc' -delete 2>/dev/null; true
