"""Deterministic statistical, spatial, and correlation analysis stages."""

from __future__ import annotations

import math
import statistics
from collections import Counter, deque
from typing import Any, Dict, Iterable, Mapping, Sequence

from .models import ParsedSTDF


ROOT_CAUSES = (
    "edge_process_stress",
    "probe_card_contamination",
    "tester_temperature_drift",
    "lithography_focus_shift",
    "random_esd_damage",
)


def data_summary(parsed: ParsedSTDF) -> Dict[str, Any]:
    test_names = sorted(
        {test_name for die in parsed.dies for test_name in die.measurements}
    )
    x_values = [die.x_coord for die in parsed.dies]
    y_values = [die.y_coord for die in parsed.dies]
    return {
        **parsed.to_summary(),
        "test_names": test_names,
        "coordinate_bounds": {
            "min_x": min(x_values),
            "max_x": max(x_values),
            "min_y": min(y_values),
            "max_y": max(y_values),
        },
        "fail_rate": parsed.failed_die_count / parsed.die_count,
    }


def _effect_size(failed_values: Sequence[float], passed_values: Sequence[float]) -> float:
    if len(failed_values) < 2 or len(passed_values) < 2:
        return 0.0
    failed_variance = statistics.variance(failed_values)
    passed_variance = statistics.variance(passed_values)
    denominator_degrees = len(failed_values) + len(passed_values) - 2
    pooled_variance = (
        (len(failed_values) - 1) * failed_variance
        + (len(passed_values) - 1) * passed_variance
    ) / denominator_degrees
    if pooled_variance <= 1e-12:
        return 0.0
    effect = (
        statistics.fmean(failed_values) - statistics.fmean(passed_values)
    ) / math.sqrt(pooled_variance)
    return max(-12.0, min(12.0, effect))


def statistical_analysis(parsed: ParsedSTDF) -> Dict[str, Any]:
    test_names = sorted(
        {test_name for die in parsed.dies for test_name in die.measurements}
    )
    tests: dict[str, dict[str, float]] = {}
    for test_name in test_names:
        failed_values = [
            float(die.measurements[test_name])
            for die in parsed.dies
            if not die.passed and test_name in die.measurements
        ]
        passed_values = [
            float(die.measurements[test_name])
            for die in parsed.dies
            if die.passed and test_name in die.measurements
        ]
        if not failed_values or not passed_values:
            continue
        tests[test_name] = {
            "failed_mean": statistics.fmean(failed_values),
            "passed_mean": statistics.fmean(passed_values),
            "effect_size": _effect_size(failed_values, passed_values),
            "failed_support": len(failed_values),
            "passed_support": len(passed_values),
        }
    ranked_tests = sorted(
        tests,
        key=lambda test_name: (-abs(tests[test_name]["effect_size"]), test_name),
    )
    return {
        "tests": tests,
        "ranked_tests": ranked_tests,
        "strong_effect_count": sum(
            abs(result["effect_size"]) >= 1.0 for result in tests.values()
        ),
    }


def _largest_component_fraction(
    failed_coordinates: set[tuple[int, int]],
) -> float:
    if not failed_coordinates:
        return 0.0
    remaining = set(failed_coordinates)
    largest_size = 0
    while remaining:
        start = remaining.pop()
        queue: deque[tuple[int, int]] = deque((start,))
        component_size = 1
        while queue:
            x_coord, y_coord = queue.popleft()
            for x_offset in (-1, 0, 1):
                for y_offset in (-1, 0, 1):
                    if x_offset == 0 and y_offset == 0:
                        continue
                    neighbor = (x_coord + x_offset, y_coord + y_offset)
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        queue.append(neighbor)
                        component_size += 1
        largest_size = max(largest_size, component_size)
    return largest_size / len(failed_coordinates)


def _quadrant_entropy(
    failed_coordinates: Iterable[tuple[int, int]],
    midpoint_x: float,
    midpoint_y: float,
) -> float:
    quadrants: Counter[tuple[bool, bool]] = Counter(
        (x_coord >= midpoint_x, y_coord >= midpoint_y)
        for x_coord, y_coord in failed_coordinates
    )
    total = sum(quadrants.values())
    if total == 0:
        return 0.0
    entropy = -sum(
        (count / total) * math.log(count / total, 2)
        for count in quadrants.values()
        if count
    )
    return entropy / 2.0


def spatial_analysis(parsed: ParsedSTDF) -> Dict[str, Any]:
    all_coordinates = {(die.x_coord, die.y_coord) for die in parsed.dies}
    failed_coordinates = {
        (die.x_coord, die.y_coord) for die in parsed.dies if not die.passed
    }
    if not failed_coordinates:
        return {
            "edge_fraction": 0.0,
            "stripe_fraction": 0.0,
            "largest_component_fraction": 0.0,
            "quadrant_entropy": 0.0,
            "pattern": "no_failures",
        }

    x_values = [coordinate[0] for coordinate in all_coordinates]
    y_values = [coordinate[1] for coordinate in all_coordinates]
    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    edge_count = sum(
        x_coord in (min_x, max_x) or y_coord in (min_y, max_y)
        for x_coord, y_coord in failed_coordinates
    )
    x_counts = Counter(x_coord for x_coord, _ in failed_coordinates)
    y_counts = Counter(y_coord for _, y_coord in failed_coordinates)
    stripe_fraction = max(max(x_counts.values()), max(y_counts.values())) / len(
        failed_coordinates
    )
    edge_fraction = edge_count / len(failed_coordinates)
    component_fraction = _largest_component_fraction(failed_coordinates)
    quadrant_entropy = _quadrant_entropy(
        failed_coordinates,
        (min_x + max_x) / 2,
        (min_y + max_y) / 2,
    )

    if edge_fraction >= 0.55:
        pattern = "peripheral_edge"
    elif stripe_fraction >= 0.45:
        pattern = "row_or_column_stripe"
    elif component_fraction >= 0.55 and quadrant_entropy < 0.80:
        pattern = "compact_cluster"
    else:
        pattern = "distributed_random"

    return {
        "edge_fraction": edge_fraction,
        "stripe_fraction": stripe_fraction,
        "largest_component_fraction": component_fraction,
        "quadrant_entropy": quadrant_entropy,
        "failed_coordinate_count": len(failed_coordinates),
        "pattern": pattern,
    }


def _pearson(values: Sequence[float], labels: Sequence[float]) -> float:
    if len(values) != len(labels) or len(values) < 2:
        return 0.0
    values_mean = statistics.fmean(values)
    labels_mean = statistics.fmean(labels)
    numerator = sum(
        (value - values_mean) * (label - labels_mean)
        for value, label in zip(values, labels)
    )
    values_variance = sum((value - values_mean) ** 2 for value in values)
    labels_variance = sum((label - labels_mean) ** 2 for label in labels)
    denominator = math.sqrt(values_variance * labels_variance)
    if denominator <= 1e-12:
        return 0.0
    return numerator / denominator


def correlation_analysis(parsed: ParsedSTDF) -> Dict[str, Any]:
    labels = [0.0 if die.passed else 1.0 for die in parsed.dies]
    test_names = sorted(
        {test_name for die in parsed.dies for test_name in die.measurements}
    )
    correlations = {
        test_name: _pearson(
            [float(die.measurements[test_name]) for die in parsed.dies],
            labels,
        )
        for test_name in test_names
        if all(test_name in die.measurements for die in parsed.dies)
    }
    ranked_tests = sorted(
        correlations,
        key=lambda test_name: (-abs(correlations[test_name]), test_name),
    )
    return {
        "correlations": correlations,
        "ranked_tests": ranked_tests,
    }


def _positive_effect(statistical: Mapping[str, Any], test_name: str) -> float:
    effect = statistical.get("tests", {}).get(test_name, {}).get("effect_size", 0.0)
    return max(0.0, min(1.0, float(effect) / 3.5))


def _negative_effect(statistical: Mapping[str, Any], test_name: str) -> float:
    effect = statistical.get("tests", {}).get(test_name, {}).get("effect_size", 0.0)
    return max(0.0, min(1.0, -float(effect) / 3.5))


def rule_scores(
    data: Mapping[str, Any],
    statistical: Mapping[str, Any],
    spatial: Mapping[str, Any],
    correlations: Mapping[str, Any],
) -> Dict[str, float]:
    edge_fraction = float(spatial.get("edge_fraction", 0.0))
    stripe_fraction = float(spatial.get("stripe_fraction", 0.0))
    cluster_fraction = float(spatial.get("largest_component_fraction", 0.0))
    entropy = float(spatial.get("quadrant_entropy", 0.0))
    fail_rate = float(data.get("fail_rate", 0.0))
    distributed_score = max(
        0.0,
        min(1.0, entropy * (1.0 - min(1.0, edge_fraction))),
    )
    sparse_score = max(0.0, 1.0 - min(1.0, fail_rate / 0.30))
    correlation_values = correlations.get("correlations", {})

    scores = {
        "edge_process_stress": (
            0.43 * edge_fraction
            + 0.27 * _positive_effect(statistical, "IDDQ")
            + 0.23 * _negative_effect(statistical, "VTH")
            + 0.07 * max(0.0, float(correlation_values.get("IDDQ", 0.0)))
        ),
        "probe_card_contamination": (
            0.43 * stripe_fraction
            + 0.37 * _positive_effect(statistical, "CONTACT_RES")
            + 0.16 * _negative_effect(statistical, "FMAX")
            + 0.04 * max(
                0.0, float(correlation_values.get("CONTACT_RES", 0.0))
            )
        ),
        "tester_temperature_drift": (
            0.43 * _positive_effect(statistical, "TEMP_SENSOR")
            + 0.34 * _negative_effect(statistical, "FMAX")
            + 0.15 * distributed_score
            + 0.08 * min(1.0, fail_rate / 0.30)
        ),
        "lithography_focus_shift": (
            0.39 * cluster_fraction
            + 0.39 * _positive_effect(statistical, "FOCUS_MON")
            + 0.17 * _positive_effect(statistical, "VTH")
            + 0.05 * (1.0 - entropy)
        ),
        "random_esd_damage": (
            0.43 * _positive_effect(statistical, "LEAKAGE")
            + 0.24 * _positive_effect(statistical, "IDDQ")
            + 0.20 * distributed_score
            + 0.13 * sparse_score
        ),
    }
    return {root_cause: max(0.0, min(1.0, score)) for root_cause, score in scores.items()}


def build_retrieval_query(
    statistical: Mapping[str, Any],
    spatial: Mapping[str, Any],
) -> str:
    descriptors = {
        "peripheral_edge": "peripheral edge failures edge distance",
        "row_or_column_stripe": "narrow row column stripe",
        "compact_cluster": "compact spatial cluster",
        "distributed_random": "distributed sparse spatially random failures",
        "no_failures": "no failures",
    }
    terms = [descriptors.get(str(spatial.get("pattern")), "failure pattern")]
    for test_name in statistical.get("ranked_tests", [])[:4]:
        effect = float(statistical["tests"][test_name]["effect_size"])
        direction = "elevated" if effect >= 0 else "reduced"
        readable_name = test_name.lower().replace("_", " ")
        terms.append(f"{direction} {readable_name}")
    return " ".join(terms)
