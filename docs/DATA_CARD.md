# Data Card: Synthetic RCA STDF v1

## Scope

This repository uses only independently generated synthetic data. It contains
no production, customer, employer, tester, product, or internal reference data.

## Inventory

| Item | Count |
|---|---:|
| STDF v4-subset files | 75 |
| Development / validation / confirmation | 30 / 20 / 25 |
| Die per file | 144 |
| Total die | 10,800 |
| Parametric measurements per die | 7 |
| Total parametric measurements | 75,600 |
| Root-cause classes | 5 |
| Independent knowledge documents | 30 |

The five synthetic causes are edge process stress, probe-card contamination,
tester temperature drift, lithography focus shift, and random ESD damage.

## Generation

`scripts/generate_synthetic_benchmark.py` builds every binary file using fixed
seeds and `backend/rca_evidence/stdf.py`. The accepted subset includes FAR, MIR,
WIR, PIR, PTR, PRR, WRR, and MRR records. Each file is 30,428 bytes and contains
144 die with seven named parametric results per die.

The top-level manifest does not contain case labels. Labels are isolated in
three hash-bound split manifests. Candidate selection reads development and
validation only; confirmation is opened after `evidence/selection.json` records
the selected policy and confirmation-manifest SHA-256.

## Isolation

- Case IDs, seeds, and scenario-family group IDs are disjoint across splits.
- Knowledge documents have separate IDs and are not copied from evaluation
  inputs.
- Ground-truth root causes are absent from STDF test names and payload text.
- Confirmation contains five cases per class.

## Provenance and License

- Provenance: independently generated synthetic data
- Generator: `synthetic-rca-v1`
- License: MIT, matching the repository license
- Corpus SHA-256:
  `cb98093f0e6ba1231e33923b3b12af367f064b74e0b9097fd5e69f09691bdbb1`

## Appropriate Use

The data supports deterministic software, retrieval, evidence-policy, parser,
and failure-recovery testing. It does not estimate performance on real STDF,
new products, new testers, process shifts, or expert failure-analysis cases.

## Known Limitations

- The STDF reader intentionally supports a bounded v4 subset, not every record.
- Root-cause signals are generated from explicit synthetic distributions.
- Files are small and uniform; large-file throughput is not claimed.
- Confirmation is finite: 25/25 correct corresponds to a 95% Wilson interval of
  86.68% to 100%, not proof of universal accuracy.
