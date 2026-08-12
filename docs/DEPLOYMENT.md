# Deployment: Evidence Runtime

## Supported Runtime

The accepted runtime is `backend/evidence_app.py`. It uses the selected
deterministic LangGraph policy, the hash-verified synthetic
knowledge corpus, and SQLite persistence.

## Local Start

```powershell
python -m pip install -r backend/requirements-evidence.txt
$env:RCA_EVIDENCE_API_KEY = "<choose-a-local-key>"
python -m uvicorn evidence_app:app --app-dir backend --host 127.0.0.1 --port 8088
```

Open `http://127.0.0.1:8088`. The UI supports sample loading, STDF upload,
six-stage traces, evidence citations, session history, and an HTML report.

## Linux Container

```powershell
docker build -f backend/Dockerfile.evidence -t project8-evidence:local .
docker run --rm -p 8088:8000 `
  -e RCA_EVIDENCE_API_KEY="<choose-a-local-key>" `
  -v project8-runtime:/home/nonroot/runtime `
  project8-evidence:local
```

Or use `docker-compose.yml` after setting `RCA_EVIDENCE_API_KEY`.
The Chainguard image runs as UID/GID 65532, uses a read-only root filesystem in Compose,
drops all capabilities, and writes only to the runtime volume.

The local workstation currently exposes a Windows-container daemon, so the Linux
image cannot be executed locally there. GitHub Actions contains the Linux build,
health, authenticated analysis, and non-root smoke gates; those remain pending
until publication triggers remote CI.

## API

| Endpoint | Authentication | Purpose |
|---|---|---|
| `GET /health` | None | Artifact identity and readiness |
| `GET /api/v1/evidence/manifest` | None | Public evidence boundary |
| `GET /api/v1/evidence/samples/DEV_001` | None | Synthetic sample download |
| `POST /api/v1/evidence/analyze` | `X-API-Key` | Bounded STDF analysis |
| `GET /api/v1/evidence/sessions` | `X-API-Key` | Persisted sessions |
| `GET /api/v1/evidence/sessions/{id}` | `X-API-Key` | Persisted result |
| `GET /api/v1/evidence/sessions/{id}/report` | `X-API-Key` | Human-readable report |

## Failure Behavior

Startup fails if the evaluated policy, model-evaluation artifact, or corpus hash
differs from `evidence/runtime_manifest.json`. Uploads fail on unsupported file
extensions, files above 8 MiB, malformed headers/records, invalid STDF version,
record/die/test limits, duplicate coordinates/tests, or nonfinite measurements.

## Not Claimed

No Kubernetes deployment, production uptime, 500-RCA/day throughput, external
LLM path, real STDF compatibility, or production SLO is accepted evidence.
