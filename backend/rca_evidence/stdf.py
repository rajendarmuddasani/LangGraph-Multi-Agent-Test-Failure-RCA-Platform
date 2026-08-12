"""Bounded reader and writer for the STDF v4 records used by this project.

The parser accepts a conservative subset of STDF v4: FAR, MIR, WIR, PIR, PTR,
PRR, WRR, and MRR. Unknown records are counted and skipped, while malformed,
oversized, or incomplete files fail closed.
"""

from __future__ import annotations

import hashlib
import math
import struct
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from .models import DieResult, ParsedSTDF


_RECORD_NAMES = {
    (0, 10): "FAR",
    (1, 10): "MIR",
    (1, 20): "MRR",
    (2, 10): "WIR",
    (2, 20): "WRR",
    (5, 10): "PIR",
    (5, 20): "PRR",
    (15, 10): "PTR",
}


class STDFParseError(ValueError):
    """Raised when an STDF input violates the accepted data contract."""


@dataclass(frozen=True)
class ParserLimits:
    """Resource and shape limits applied before parsed data reaches agents."""

    max_file_bytes: int = 8 * 1024 * 1024
    max_records: int = 100_000
    max_dies: int = 10_000
    max_tests_per_die: int = 128
    max_coordinate_abs: int = 32_767


def _record(record_type: int, record_subtype: int, body: bytes) -> bytes:
    if len(body) > 65_535:
        raise ValueError("STDF record body exceeds the unsigned 16-bit limit")
    return struct.pack("<HBB", len(body), record_type, record_subtype) + body


def _encode_cn(value: str) -> bytes:
    encoded = value.encode("ascii")
    if len(encoded) > 255:
        raise ValueError("STDF Cn value exceeds 255 bytes")
    return bytes((len(encoded),)) + encoded


def _read_cn(body: memoryview, offset: int) -> tuple[str, int]:
    if offset >= len(body):
        raise STDFParseError("Truncated STDF Cn length")
    length = int(body[offset])
    start = offset + 1
    end = start + length
    if end > len(body):
        raise STDFParseError("Truncated STDF Cn value")
    try:
        value = bytes(body[start:end]).decode("ascii")
    except UnicodeDecodeError as exc:
        raise STDFParseError("STDF Cn value is not ASCII") from exc
    return value, end


def _encode_bn(value: bytes = b"") -> bytes:
    if len(value) > 255:
        raise ValueError("STDF Bn value exceeds 255 bytes")
    return bytes((len(value),)) + value


def build_stdf_bytes(
    lot_id: str,
    wafer_id: str,
    dies: Iterable[DieResult],
    *,
    start_time: int = 1_700_000_000,
) -> bytes:
    """Build a deterministic STDF v4 byte stream from synthetic die results."""

    ordered_dies = sorted(dies, key=lambda die: (die.y_coord, die.x_coord))
    records: list[bytes] = []

    records.append(_record(0, 10, struct.pack("<BB", 2, 4)))

    mir_fixed = struct.pack(
        "<IIBcccHc",
        start_time,
        start_time,
        1,
        b"P",
        b" ",
        b" ",
        0,
        b" ",
    )
    mir_text = [
        lot_id,
        "SYNTHETIC_DEVICE",
        "LOCAL_NODE",
        "SYNTHETIC_TESTER",
        "RCA_BENCHMARK",
        "1",
    ] + [""] * 24
    records.append(_record(1, 10, mir_fixed + b"".join(_encode_cn(value) for value in mir_text)))

    wir_body = struct.pack("<BBI", 1, 1, start_time) + _encode_cn(wafer_id)
    records.append(_record(2, 10, wir_body))

    good_count = 0
    for die_index, die in enumerate(ordered_dies, start=1):
        records.append(_record(5, 10, struct.pack("<BB", 1, 1)))
        for test_number, (test_name, result) in enumerate(
            sorted(die.measurements.items()), start=10_000
        ):
            if not math.isfinite(float(result)):
                raise ValueError(f"Non-finite test result for {test_name}")
            test_flag = 0 if die.passed else 0x80
            ptr_body = struct.pack(
                "<IBBBBf",
                test_number,
                1,
                1,
                test_flag,
                0,
                float(result),
            )
            ptr_body += _encode_cn(test_name) + _encode_cn("")
            records.append(_record(15, 10, ptr_body))

        if die.passed:
            good_count += 1
        part_flag = 0 if die.passed else 0x08
        part_id = die.part_id or f"DIE_{die_index:04d}"
        prr_body = struct.pack(
            "<BBBHHHhhI",
            1,
            1,
            part_flag,
            len(die.measurements),
            die.hard_bin,
            die.soft_bin,
            die.x_coord,
            die.y_coord,
            10,
        )
        prr_body += _encode_cn(part_id) + _encode_cn("") + _encode_bn()
        records.append(_record(5, 20, prr_body))

    finish_time = start_time + max(1, len(ordered_dies))
    wrr_body = struct.pack(
        "<BBIIIIII",
        1,
        1,
        finish_time,
        len(ordered_dies),
        0,
        0,
        good_count,
        len(ordered_dies),
    )
    wrr_body += b"".join(_encode_cn(value) for value in (wafer_id, "", "", "", "", ""))
    records.append(_record(2, 20, wrr_body))

    mrr_body = struct.pack("<Ic", finish_time, b" ") + _encode_cn("") + _encode_cn("")
    records.append(_record(1, 20, mrr_body))
    return b"".join(records)


def parse_stdf_bytes(data: bytes, limits: ParserLimits | None = None) -> ParsedSTDF:
    """Parse and validate the accepted STDF v4 subset from an in-memory file."""

    active_limits = limits or ParserLimits()
    if not data:
        raise STDFParseError("STDF input is empty")
    if len(data) > active_limits.max_file_bytes:
        raise STDFParseError(
            f"STDF input exceeds {active_limits.max_file_bytes} byte limit"
        )

    offset = 0
    record_index = 0
    record_counts: Counter[str] = Counter()
    lot_id = ""
    wafer_id = ""
    far_seen = False
    mir_seen = False
    mrr_seen = False
    pending_measurements: dict[str, float] = {}
    dies: list[DieResult] = []
    coordinates: set[tuple[int, int]] = set()

    while offset < len(data):
        if len(data) - offset < 4:
            raise STDFParseError(f"Truncated STDF record header at byte {offset}")
        record_length, record_type, record_subtype = struct.unpack_from(
            "<HBB", data, offset
        )
        offset += 4
        record_end = offset + record_length
        if record_end > len(data):
            raise STDFParseError(
                f"Truncated STDF record body at record {record_index + 1}"
            )
        body = memoryview(data)[offset:record_end]
        offset = record_end
        record_index += 1
        if record_index > active_limits.max_records:
            raise STDFParseError("STDF record count exceeds configured limit")

        record_name = _RECORD_NAMES.get(
            (record_type, record_subtype),
            f"UNKNOWN_{record_type}_{record_subtype}",
        )
        record_counts[record_name] += 1

        if record_index == 1 and record_name != "FAR":
            raise STDFParseError("First STDF record must be FAR")

        if record_name == "FAR":
            if far_seen or len(body) != 2:
                raise STDFParseError("Invalid or duplicate FAR record")
            cpu_type, stdf_version = struct.unpack_from("<BB", body, 0)
            if cpu_type != 2 or stdf_version != 4:
                raise STDFParseError(
                    "Only little-endian STDF v4 files are accepted"
                )
            far_seen = True
        elif record_name == "MIR":
            if len(body) < 16:
                raise STDFParseError("MIR record is too short")
            lot_id, _ = _read_cn(body, 15)
            if not lot_id:
                raise STDFParseError("MIR lot identifier is empty")
            mir_seen = True
        elif record_name == "WIR":
            if len(body) < 7:
                raise STDFParseError("WIR record is too short")
            wafer_id, _ = _read_cn(body, 6)
            if not wafer_id:
                raise STDFParseError("WIR wafer identifier is empty")
        elif record_name == "PIR":
            if pending_measurements:
                raise STDFParseError("PIR encountered before prior part was closed")
        elif record_name == "PTR":
            if len(body) < 13:
                raise STDFParseError("PTR record is too short")
            result = float(struct.unpack_from("<f", body, 8)[0])
            if not math.isfinite(result):
                raise STDFParseError("PTR result is not finite")
            test_name, _ = _read_cn(body, 12)
            if not test_name:
                raise STDFParseError("PTR test name is empty")
            if test_name in pending_measurements:
                raise STDFParseError(f"Duplicate PTR test name: {test_name}")
            pending_measurements[test_name] = result
            if len(pending_measurements) > active_limits.max_tests_per_die:
                raise STDFParseError("Tests per die exceed configured limit")
        elif record_name == "PRR":
            if len(body) < 18:
                raise STDFParseError("PRR record is too short")
            (
                _head_number,
                _site_number,
                _part_flag,
                declared_test_count,
                hard_bin,
                soft_bin,
                x_coord,
                y_coord,
                _test_time,
            ) = struct.unpack_from("<BBBHHHhhI", body, 0)
            part_id, _ = _read_cn(body, 17)
            if declared_test_count != len(pending_measurements):
                raise STDFParseError(
                    "PRR test count does not match preceding PTR records"
                )
            if abs(x_coord) > active_limits.max_coordinate_abs or abs(
                y_coord
            ) > active_limits.max_coordinate_abs:
                raise STDFParseError("Die coordinate exceeds configured limit")
            coordinate = (x_coord, y_coord)
            if coordinate in coordinates:
                raise STDFParseError(f"Duplicate die coordinate: {coordinate}")
            coordinates.add(coordinate)
            passed = hard_bin == 1 and soft_bin == 1
            dies.append(
                DieResult(
                    x_coord=x_coord,
                    y_coord=y_coord,
                    hard_bin=hard_bin,
                    soft_bin=soft_bin,
                    passed=passed,
                    measurements=dict(pending_measurements),
                    part_id=part_id,
                )
            )
            pending_measurements.clear()
            if len(dies) > active_limits.max_dies:
                raise STDFParseError("Die count exceeds configured limit")
        elif record_name == "MRR":
            mrr_seen = True

    if pending_measurements:
        raise STDFParseError("STDF ended before pending PTR records reached PRR")
    if not far_seen or not mir_seen or not wafer_id or not mrr_seen:
        raise STDFParseError("STDF is missing FAR, MIR, WIR, or MRR records")
    if not dies:
        raise STDFParseError("STDF contains no completed die records")

    return ParsedSTDF(
        lot_id=lot_id,
        wafer_id=wafer_id,
        dies=tuple(dies),
        file_sha256=hashlib.sha256(data).hexdigest(),
        record_counts=dict(sorted(record_counts.items())),
        byte_count=len(data),
    )
