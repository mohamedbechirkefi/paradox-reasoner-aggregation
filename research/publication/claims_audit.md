<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Claims audit

Status at M4 (2026-11-25): audited. `research/claims_register.csv` has 24 rows: CLM-001 to CLM-016 (results: 10 confirmatory, 2 descriptive, 3 exploratory, 1 exploratory diagnostic) and CLM-E01 to CLM-E08 (external). Full record: `evidence_audit.md`; second pass: `review_pass_2.md`.

For every row of the claims register:

- [ ] Claim text matches the manuscript, reports, README, demo and articles word for word in scope. **Manuscript and reports: checked in M4. README, demo and articles: M5.**
- [x] Type is correct (verification, primary, prediction test, sensitivity, robustness, descriptive, exploratory, external).
- [x] Evidence path exists and resolves to a result file, run id and figure or table id (`artifact_manifest.json`, built by `scripts/m4_build_manifest.py`).
- [x] Number recomputed from raw output; denominator, unit, precision, interval and sample count checked (`scripts/m4_recompute_checks.py`: 31 of 31 pass; one mismatch fixed in CLM-002, D-014).
- [x] External claims map to a source listed as verified in `literature_review.md`; abstract-only sources are marked.
- [x] Limitations column filled; synthetic scope stated.
- [x] Second-pass review challenged the preferred hypothesis (AI assistant, 2026-11-25, `review_pass_2.md`). Owner review pending.

Claims removed or qualified in M4: CLM-002 (split corrected to 20 MV and 12 SEQ); CLM-010 (limitation added: 15 of 18 checks insensitive by construction). The manuscript's general statements "pairwise statistics do not decide whether aggregation helps" and the practical-significance advice were qualified or removed because no row supported them in general form (review pass R6, R7).
