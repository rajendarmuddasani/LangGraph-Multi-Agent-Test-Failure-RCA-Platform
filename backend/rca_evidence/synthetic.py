"""Independent deterministic synthetic benchmark generation.

No internal, customer, or production data is used. Ground-truth labels live only
in the manifest consumed by evaluation; they are not encoded in STDF test text.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping

from .models import DieResult
from .stdf import build_stdf_bytes


GENERATOR_VERSION = "synthetic-rca-v1"
GRID_SIZE = 12
ROOT_CAUSES = (
    "edge_process_stress",
    "probe_card_contamination",
    "tester_temperature_drift",
    "lithography_focus_shift",
    "random_esd_damage",
)
SPLIT_CASES_PER_CAUSE = {
    "development": 6,
    "validation": 4,
    "confirmation": 5,
}


@dataclass(frozen=True)
class CaseDefinition:
    case_id: str
    split: str
    group_id: str
    expected_root_cause: str
    seed: int
    ambiguous: bool


_BASE_MEASUREMENTS = {
    "CONTACT_RES": (0.10, 0.012),
    "FMAX": (1000.0, 18.0),
    "FOCUS_MON": (0.0, 0.22),
    "IDDQ": (100.0, 4.5),
    "LEAKAGE": (1.0, 0.12),
    "TEMP_SENSOR": (25.0, 0.35),
    "VTH": (0.72, 0.012),
}

_EFFECTS = {
    "edge_process_stress": {"IDDQ": 32.0, "VTH": -0.075, "FMAX": -45.0},
    "probe_card_contamination": {"CONTACT_RES": 0.30, "FMAX": -95.0},
    "tester_temperature_drift": {"TEMP_SENSOR": 7.5, "FMAX": -135.0, "IDDQ": 10.0},
    "lithography_focus_shift": {"FOCUS_MON": 2.2, "VTH": 0.060},
    "random_esd_damage": {"LEAKAGE": 3.4, "IDDQ": 17.0},
}

_CORPUS_TEMPLATES = {
    "edge_process_stress": (
        "Peripheral edge failures with high IDDQ and depressed VTH indicate edge process stress. "
        "Confirm with edge-distance concentration and cross-section review."
    ),
    "probe_card_contamination": (
        "A narrow row or column stripe with elevated contact resistance and reduced FMAX is consistent "
        "with probe card contamination. Clean and re-qualify the probe interface."
    ),
    "tester_temperature_drift": (
        "Distributed failures with elevated temperature sensor readings and FMAX loss indicate tester "
        "temperature drift. Verify thermal control and chamber calibration."
    ),
    "lithography_focus_shift": (
        "A compact spatial cluster with a strong focus monitor and VTH shift is consistent with a "
        "lithography focus excursion. Review focus maps and reticle position."
    ),
    "random_esd_damage": (
        "Sparse spatially random failures with leakage and IDDQ elevation indicate random ESD damage. "
        "Inspect handling controls and perform electrical failure analysis."
    ),
}


def case_definitions() -> List[CaseDefinition]:
    """Return all split-isolated benchmark cases in deterministic order."""

    definitions: list[CaseDefinition] = []
    split_offsets = {"development": 10_000, "validation": 20_000, "confirmation": 30_000}
    split_prefixes = {"development": "DEV", "validation": "VAL", "confirmation": "CNF"}
    for split, cases_per_cause in SPLIT_CASES_PER_CAUSE.items():
        serial = 1
        for cause_index, root_cause in enumerate(ROOT_CAUSES):
            for case_index in range(cases_per_cause):
                seed = split_offsets[split] + cause_index * 100 + case_index
                definitions.append(
                    CaseDefinition(
                        case_id=f"{split_prefixes[split]}_{serial:03d}",
                        split=split,
                        group_id=f"{split_prefixes[split]}_G{cause_index + 1}_{case_index + 1}",
                        expected_root_cause=root_cause,
                        seed=seed,
                        ambiguous=case_index == cases_per_cause - 1,
                    )
                )
                serial += 1
    return definitions


def _affected_probability(
    root_cause: str,
    x_coord: int,
    y_coord: int,
    random_source: random.Random,
    seed: int,
) -> float:
    edge_distance = min(
        x_coord,
        y_coord,
        GRID_SIZE - 1 - x_coord,
        GRID_SIZE - 1 - y_coord,
    )
    if root_cause == "edge_process_stress":
        return 0.78 if edge_distance == 0 else 0.44 if edge_distance == 1 else 0.025
    if root_cause == "probe_card_contamination":
        stripe_coord = 3 + seed % 6
        distance = abs(x_coord - stripe_coord)
        return 0.74 if distance == 0 else 0.24 if distance == 1 else 0.02
    if root_cause == "tester_temperature_drift":
        return 0.23 + 0.06 * random_source.random()
    if root_cause == "lithography_focus_shift":
        center_x = 3 if seed % 2 == 0 else 8
        center_y = 3 if (seed // 2) % 2 == 0 else 8
        radius_squared = (x_coord - center_x) ** 2 + (y_coord - center_y) ** 2
        return 0.78 if radius_squared <= 4 else 0.25 if radius_squared <= 10 else 0.02
    if root_cause == "random_esd_damage":
        return 0.10 + 0.03 * random_source.random()
    raise ValueError(f"Unknown root cause: {root_cause}")


def generate_case_dies(case: CaseDefinition) -> List[DieResult]:
    """Generate a deterministic 12x12 wafer for one labeled scenario."""

    # Deterministic synthetic generation, not a security boundary.
    random_source = random.Random(case.seed)  # nosec B311
    cause_index = ROOT_CAUSES.index(case.expected_root_cause)
    secondary_cause = ROOT_CAUSES[(cause_index + 1) % len(ROOT_CAUSES)]
    dies: list[DieResult] = []

    for y_coord in range(GRID_SIZE):
        for x_coord in range(GRID_SIZE):
            probability = _affected_probability(
                case.expected_root_cause,
                x_coord,
                y_coord,
                random_source,
                case.seed,
            )
            failed = random_source.random() < probability
            measurements: dict[str, float] = {
                test_name: random_source.gauss(mean, standard_deviation)
                for test_name, (mean, standard_deviation) in _BASE_MEASUREMENTS.items()
            }
            if failed:
                for test_name, effect in _EFFECTS[case.expected_root_cause].items():
                    measurements[test_name] += effect * random_source.uniform(0.82, 1.18)
                if case.ambiguous:
                    for test_name, effect in _EFFECTS[secondary_cause].items():
                        measurements[test_name] += effect * random_source.uniform(0.28, 0.42)

            dies.append(
                DieResult(
                    x_coord=x_coord,
                    y_coord=y_coord,
                    hard_bin=5 if failed else 1,
                    soft_bin=5 if failed else 1,
                    passed=not failed,
                    measurements={
                        test_name: round(value, 6)
                        for test_name, value in measurements.items()
                    },
                    part_id=f"D{x_coord:02d}{y_coord:02d}",
                )
            )
    return dies


def generate_case_bytes(case: CaseDefinition) -> bytes:
    """Generate one deterministic STDF file without exposing its label in-band."""

    return build_stdf_bytes(
        lot_id=f"SYNTH_{case.case_id}",
        wafer_id="W01",
        dies=generate_case_dies(case),
        start_time=1_700_000_000 + case.seed,
    )


def build_knowledge_corpus() -> List[Dict[str, Any]]:
    """Create 30 independent synthetic RCA knowledge documents."""

    corpus: list[dict[str, Any]] = []
    for cause_index, root_cause in enumerate(ROOT_CAUSES):
        for document_index in range(6):
            corpus.append(
                {
                    "document_id": f"KB_{cause_index + 1}_{document_index + 1:02d}",
                    "root_cause": root_cause,
                    "title": root_cause.replace("_", " ").title(),
                    "text": (
                        f"Synthetic reference case {document_index + 1}. "
                        f"{_CORPUS_TEMPLATES[root_cause]} "
                        f"Evidence family REF_{cause_index + 1}_{document_index + 1}."
                    ),
                    "provenance": "independently_generated_synthetic",
                    "license": "MIT",
                }
            )
    return corpus


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def generate_dataset(output_root: Path) -> Dict[str, Any]:
    """Write deterministic STDF files, corpus, and a hash-bound manifest."""

    output_root.mkdir(parents=True, exist_ok=True)
    cases_root = output_root / "cases"
    manifest_cases: list[dict[str, Any]] = []

    for case in case_definitions():
        split_root = cases_root / case.split
        split_root.mkdir(parents=True, exist_ok=True)
        payload = generate_case_bytes(case)
        relative_path = Path("cases") / case.split / f"{case.case_id}.stdf"
        (output_root / relative_path).write_bytes(payload)
        case_entry = asdict(case)
        case_entry.update(
            {
                "relative_path": relative_path.as_posix(),
                "file_sha256": hashlib.sha256(payload).hexdigest(),
                "byte_count": len(payload),
                "die_count": GRID_SIZE * GRID_SIZE,
                "measurement_count": GRID_SIZE
                * GRID_SIZE
                * len(_BASE_MEASUREMENTS),
            }
        )
        manifest_cases.append(case_entry)

    corpus = build_knowledge_corpus()
    corpus_bytes = _canonical_json_bytes(corpus)
    (output_root / "corpus.json").write_bytes(corpus_bytes)

    manifests_root = output_root / "manifests"
    manifests_root.mkdir(parents=True, exist_ok=True)
    split_manifests: dict[str, dict[str, Any]] = {}
    split_counts: dict[str, int] = {}
    for split in SPLIT_CASES_PER_CAUSE:
        split_cases = [case for case in manifest_cases if case["split"] == split]
        split_payload = {
            "schema_version": 1,
            "generator_version": GENERATOR_VERSION,
            "split": split,
            "case_count": len(split_cases),
            "cases": split_cases,
        }
        split_bytes = _canonical_json_bytes(split_payload)
        relative_path = Path("manifests") / f"{split}.json"
        (output_root / relative_path).write_bytes(split_bytes)
        split_counts[split] = len(split_cases)
        split_manifests[split] = {
            "relative_path": relative_path.as_posix(),
            "sha256": hashlib.sha256(split_bytes).hexdigest(),
            "case_count": len(split_cases),
        }
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "generator_version": GENERATOR_VERSION,
        "provenance": "independently_generated_synthetic",
        "license": "MIT",
        "root_causes": list(ROOT_CAUSES),
        "split_strategy": "disjoint case and scenario-family groups",
        "split_counts": split_counts,
        "case_count": len(manifest_cases),
        "knowledge_document_count": len(corpus),
        "die_count": sum(case["die_count"] for case in manifest_cases),
        "measurement_count": sum(
            case["measurement_count"] for case in manifest_cases
        ),
        "corpus_sha256": hashlib.sha256(corpus_bytes).hexdigest(),
        "split_manifests": split_manifests,
    }
    manifest_bytes = _canonical_json_bytes(manifest)
    (output_root / "manifest.json").write_bytes(manifest_bytes)
    return manifest


def load_manifest(output_root: Path) -> Mapping[str, Any]:
    return json.loads((output_root / "manifest.json").read_text(encoding="utf-8"))


def load_split_manifest(output_root: Path, split: str) -> Mapping[str, Any]:
    if split not in SPLIT_CASES_PER_CAUSE:
        raise ValueError(f"Unknown benchmark split: {split}")
    return json.loads(
        (output_root / "manifests" / f"{split}.json").read_text(
            encoding="utf-8"
        )
    )
