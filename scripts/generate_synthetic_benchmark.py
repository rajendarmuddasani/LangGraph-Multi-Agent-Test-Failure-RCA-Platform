#!/usr/bin/env python
"""Generate the independently created Project 08 STDF benchmark."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from rca_evidence.synthetic import generate_dataset  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=REPOSITORY_ROOT / "data" / "synthetic_rca_v1",
    )
    arguments = parser.parse_args()
    manifest = generate_dataset(arguments.output)
    print(
        json.dumps(
            {
                "output": str(arguments.output),
                "case_count": manifest["case_count"],
                "split_counts": manifest["split_counts"],
                "die_count": manifest["die_count"],
                "measurement_count": manifest["measurement_count"],
                "knowledge_document_count": manifest["knowledge_document_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
