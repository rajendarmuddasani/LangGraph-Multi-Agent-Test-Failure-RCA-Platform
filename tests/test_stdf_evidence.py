"""Contract tests for deterministic synthetic STDF ingestion."""

from __future__ import annotations

import hashlib

import pytest

from rca_evidence.models import DieResult
from rca_evidence.stdf import (
    ParserLimits,
    STDFParseError,
    build_stdf_bytes,
    parse_stdf_bytes,
)


def _sample_dies() -> list[DieResult]:
    return [
        DieResult(0, 0, 1, 1, True, {"IDDQ": 101.0, "VTH": 0.72}, "D1"),
        DieResult(1, 0, 5, 5, False, {"IDDQ": 141.0, "VTH": 0.63}, "D2"),
        DieResult(0, 1, 1, 1, True, {"IDDQ": 99.0, "VTH": 0.73}, "D3"),
        DieResult(1, 1, 5, 5, False, {"IDDQ": 138.0, "VTH": 0.65}, "D4"),
    ]


def test_stdf_round_trip_preserves_die_measurements() -> None:
    payload = build_stdf_bytes("SYNTH_LOT_001", "W01", _sample_dies())
    parsed = parse_stdf_bytes(payload)

    assert parsed.lot_id == "SYNTH_LOT_001"
    assert parsed.wafer_id == "W01"
    assert parsed.die_count == 4
    assert parsed.failed_die_count == 2
    assert parsed.yield_rate == 0.5
    assert parsed.file_sha256 == hashlib.sha256(payload).hexdigest()
    assert parsed.dies[1].measurements["IDDQ"] == pytest.approx(141.0)
    assert parsed.record_counts["PTR"] == 8


def test_stdf_writer_is_deterministic() -> None:
    first = build_stdf_bytes("SYNTH_LOT_001", "W01", _sample_dies())
    second = build_stdf_bytes("SYNTH_LOT_001", "W01", _sample_dies())
    assert first == second


@pytest.mark.parametrize(
    "mutator, message",
    [
        (lambda payload: payload[:-3], "Truncated STDF record body"),
        (
            lambda payload: payload[:5] + bytes((3,)) + payload[6:],
            "Only little-endian STDF v4 files are accepted",
        ),
    ],
)
def test_stdf_parser_rejects_corruption(mutator, message: str) -> None:
    payload = build_stdf_bytes("SYNTH_LOT_001", "W01", _sample_dies())
    with pytest.raises(STDFParseError, match=message):
        parse_stdf_bytes(mutator(payload))


def test_stdf_parser_enforces_file_limit() -> None:
    payload = build_stdf_bytes("SYNTH_LOT_001", "W01", _sample_dies())
    with pytest.raises(STDFParseError, match="exceeds"):
        parse_stdf_bytes(payload, ParserLimits(max_file_bytes=16))
