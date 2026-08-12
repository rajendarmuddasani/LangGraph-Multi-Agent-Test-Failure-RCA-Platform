#!/usr/bin/env python
"""Render reproducible benchmark assets from canonical evidence and STDF data."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rca_evidence.stdf import parse_stdf_bytes  # noqa: E402


COLORS = {
    "navy": "#10243A",
    "teal": "#0F8A83",
    "yellow": "#F2C14E",
    "coral": "#E76F51",
    "blue": "#2F6FED",
    "violet": "#6D5BD0",
    "paper": "#F7F8FB",
}


def render_candidate_comparison(output_path: Path) -> None:
    evidence = json.loads(
        (REPOSITORY_ROOT / "evidence" / "candidate_results.json").read_text(
            encoding="utf-8"
        )
    )
    candidates = evidence["candidates"]
    labels = [
        candidate["aggregate"]["policy_id"].replace("_v1", "").replace("_", "\n")
        for candidate in candidates
    ]
    accuracy = [candidate["aggregate"]["cause_accuracy"] for candidate in candidates]
    coverage = [candidate["aggregate"]["automatic_coverage"] for candidate in candidates]
    evidence_diversity = [
        candidate["aggregate"]["mean_evidence_source_diversity"] / 4.0
        for candidate in candidates
    ]

    figure, axis = plt.subplots(figsize=(14, 7.5), dpi=120)
    figure.patch.set_facecolor(COLORS["paper"])
    axis.set_facecolor("white")
    positions = list(range(len(candidates)))
    width = 0.23
    axis.bar(
        [position - width for position in positions],
        accuracy,
        width,
        label="Cause accuracy",
        color=COLORS["teal"],
    )
    axis.bar(
        positions,
        coverage,
        width,
        label="Automatic coverage",
        color=COLORS["yellow"],
    )
    axis.bar(
        [position + width for position in positions],
        evidence_diversity,
        width,
        label="Evidence diversity / 4",
        color=COLORS["blue"],
    )
    axis.set_ylim(0, 1.08)
    axis.set_xticks(positions, labels)
    axis.set_ylabel("Validation score")
    axis.set_title(
        "Frozen validation candidates",
        color=COLORS["navy"],
        fontsize=20,
        fontweight="bold",
        pad=16,
    )
    axis.grid(axis="y", alpha=0.22)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(loc="lower left", ncols=3, frameon=False)
    axis.text(
        0.99,
        0.02,
        "20 validation cases | selected: fusion_balanced_v1",
        transform=axis.transAxes,
        ha="right",
        va="bottom",
        color="#506275",
    )
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


def render_wafer_map(output_path: Path) -> None:
    sample_path = (
        REPOSITORY_ROOT
        / "data"
        / "synthetic_rca_v1"
        / "cases"
        / "development"
        / "DEV_001.stdf"
    )
    parsed = parse_stdf_bytes(sample_path.read_bytes())
    passed_x = [die.x_coord for die in parsed.dies if die.passed]
    passed_y = [die.y_coord for die in parsed.dies if die.passed]
    failed_x = [die.x_coord for die in parsed.dies if not die.passed]
    failed_y = [die.y_coord for die in parsed.dies if not die.passed]

    figure, axis = plt.subplots(figsize=(9, 8), dpi=130)
    figure.patch.set_facecolor(COLORS["paper"])
    axis.set_facecolor("white")
    axis.scatter(
        passed_x,
        passed_y,
        s=210,
        marker="s",
        color="#B9DDD8",
        edgecolor="white",
        linewidth=0.7,
        label="Pass",
    )
    axis.scatter(
        failed_x,
        failed_y,
        s=210,
        marker="s",
        color=COLORS["coral"],
        edgecolor="white",
        linewidth=0.7,
        label="Fail",
    )
    axis.set_aspect("equal")
    axis.invert_yaxis()
    axis.set_xticks(range(12))
    axis.set_yticks(range(12))
    axis.set_xlabel("Die X")
    axis.set_ylabel("Die Y")
    axis.set_title(
        "Parsed synthetic STDF wafer map",
        color=COLORS["navy"],
        fontsize=19,
        fontweight="bold",
        pad=14,
    )
    axis.text(
        0.0,
        -0.10,
        f"DEV_001 | {parsed.die_count} die | {parsed.failed_die_count} fail | sha256 {parsed.file_sha256[:12]}...",
        transform=axis.transAxes,
        color="#506275",
    )
    axis.legend(frameon=False, loc="upper center", ncols=2)
    axis.spines[["top", "right"]].set_visible(False)
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


def render_favicon(output_path: Path) -> None:
    image = Image.new("RGBA", (64, 64), COLORS["navy"])
    draw = ImageDraw.Draw(image)
    for index, color in enumerate(
        (COLORS["teal"], COLORS["blue"], COLORS["violet"], COLORS["coral"])
    ):
        offset = 8 + index * 12
        draw.rounded_rectangle(
            (offset, 12, offset + 8, 52),
            radius=2,
            fill=color,
        )
    draw.rectangle((8, 48, 56, 55), fill=COLORS["yellow"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="ICO", sizes=[(16, 16), (32, 32), (64, 64)])


def main() -> int:
    assets_root = REPOSITORY_ROOT / "evidence" / "assets"
    render_candidate_comparison(assets_root / "candidate_comparison.png")
    render_wafer_map(assets_root / "sample_wafer_map.png")
    render_favicon(REPOSITORY_ROOT / "favicon.ico")
    print(
        json.dumps(
            {
                "candidate_comparison": str(assets_root / "candidate_comparison.png"),
                "sample_wafer_map": str(assets_root / "sample_wafer_map.png"),
                "favicon": str(REPOSITORY_ROOT / "favicon.ico"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
