# Security and Privacy Boundary

## Input Controls

- Accepts `.stdf` multipart uploads only.
- Rejects files above 8 MiB before parsing.
- Requires little-endian STDF v4 FAR and the expected lifecycle records.
- Applies record, die, test-per-die, coordinate, duplicate, and finite-value
  limits.
- Never executes uploaded content or uses user-controlled filesystem paths.

## API Controls

- Analysis, session, and report routes require `X-API-Key`.
- API keys are supplied only through `RCA_EVIDENCE_API_KEY`; no key is committed.
- Key comparison uses `hmac.compare_digest`.
- Missing key configuration fails protected routes with HTTP 503.

## Runtime Integrity

- The selected policy must match the confirmed evaluation artifact.
- Evaluation JSON and BM25 corpus SHA-256 values are verified at startup.
- Sessions and complete stage traces are stored in local SQLite.
- External LLM calls are disabled in the accepted path.

## Container Controls

- Runtime user is Chainguard nonroot UID/GID 65532.
- Compose drops all Linux capabilities and enables `no-new-privileges`.
- Root filesystem is read-only; `/tmp` is bounded and persistence uses one
  explicit volume.
- The runtime image installs only FastAPI, Uvicorn, and multipart parsing.

## Privacy

The committed benchmark and knowledge corpus are independently generated
synthetic data. Public files contain no internal URLs, credentials, identifiers,
production logs, customer data, or employer-source data.

## Residual Risks

- API-key authentication is appropriate for a local reference runtime, not a
  complete enterprise identity/RBAC solution.
- The parser supports a bounded STDF subset and needs fuzzing before exposure to
  untrusted internet traffic.
- Local SQLite is not a high-availability datastore.
- Dependency vulnerability status must be rechecked in remote CI before release.
