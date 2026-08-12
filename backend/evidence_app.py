"""Minimal hash-bound FastAPI runtime for the accepted Project 08 evidence path."""

from __future__ import annotations

import hmac
import os
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

from rca_evidence.reporting import render_report_html
from rca_evidence.runtime import RuntimeBundle
from rca_evidence.stdf import STDFParseError


MAX_UPLOAD_BYTES = 8 * 1024 * 1024
DEFAULT_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def create_app(
    *,
    repository_root: Path | None = None,
    database_path: Path | None = None,
    api_key: str | None = None,
) -> FastAPI:
    root = (repository_root or DEFAULT_REPOSITORY_ROOT).resolve()
    active_database = database_path or Path(
        os.environ.get(
            "RCA_EVIDENCE_DATABASE",
            root / "runtime" / "rca_sessions.sqlite3",
        )
    )
    configured_key = api_key if api_key is not None else os.environ.get(
        "RCA_EVIDENCE_API_KEY"
    )
    bundle = RuntimeBundle(root, active_database)

    application = FastAPI(
        title="Evidence-Backed Synthetic STDF RCA",
        version="1.0.0",
        description=(
            "Hash-bound deterministic RCA runtime for independently generated "
            "synthetic STDF v4-subset files."
        ),
    )
    application.state.bundle = bundle
    application.state.api_key_configured = configured_key is not None

    def require_api_key(
        x_api_key: Annotated[str | None, Header()] = None,
    ) -> None:
        if configured_key is None:
            raise HTTPException(
                status_code=503,
                detail="RCA_EVIDENCE_API_KEY is not configured",
            )
        if x_api_key is None or not hmac.compare_digest(x_api_key, configured_key):
            raise HTTPException(status_code=401, detail="Invalid API key")

    @application.get("/", response_class=HTMLResponse)
    def user_interface() -> FileResponse:
        return FileResponse(root / "backend" / "evidence_static" / "index.html")

    @application.get("/favicon.ico", include_in_schema=False)
    def favicon() -> FileResponse:
        return FileResponse(root / "favicon.ico", media_type="image/x-icon")

    @application.get("/health")
    def health() -> dict:
        return {
            **bundle.health_summary(),
            "api_key_configured": configured_key is not None,
        }

    @application.get("/api/v1/evidence/manifest")
    def manifest() -> dict:
        return {
            **bundle.health_summary(),
            "data_scope": "independently_generated_synthetic",
            "production_slo": False,
        }

    @application.get(
        "/api/v1/evidence/samples/{case_id}",
        response_class=FileResponse,
    )
    def sample(case_id: str) -> FileResponse:
        if case_id != "DEV_001":
            raise HTTPException(status_code=404, detail="Sample not found")
        sample_path = root / "data" / "synthetic_rca_v1" / "cases" / "development" / "DEV_001.stdf"
        return FileResponse(
            sample_path,
            media_type="application/octet-stream",
            filename="DEV_001.stdf",
        )

    @application.post(
        "/api/v1/evidence/analyze",
        dependencies=[Depends(require_api_key)],
    )
    async def analyze(file: Annotated[UploadFile, File()]) -> dict:
        filename = file.filename or ""
        if not filename.lower().endswith(".stdf"):
            raise HTTPException(status_code=415, detail="Only .stdf files are accepted")
        payload = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(payload) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="STDF upload exceeds 8 MiB")
        try:
            result = bundle.workflow.analyze(payload)
        except STDFParseError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid STDF input: {exc}",
            ) from exc
        return result.to_dict()

    @application.get(
        "/api/v1/evidence/sessions",
        dependencies=[Depends(require_api_key)],
    )
    def sessions(limit: int = 20) -> list[dict]:
        try:
            return bundle.store.list_sessions(limit)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @application.get(
        "/api/v1/evidence/sessions/{session_id}",
        dependencies=[Depends(require_api_key)],
    )
    def session(session_id: str) -> dict:
        result = bundle.store.get(session_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return result

    @application.get(
        "/api/v1/evidence/sessions/{session_id}/report",
        response_class=HTMLResponse,
        dependencies=[Depends(require_api_key)],
    )
    def report(session_id: str) -> HTMLResponse:
        result = bundle.store.get(session_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return HTMLResponse(render_report_html(result))

    return application


app = create_app()
