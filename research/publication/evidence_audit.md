<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Evidence audit (M4, master prompt section 11.5)

- **Date:** 2026-11-25.
- **Scope:** `research/paper/manuscript.md`, `research/paper/supplementary.md`, the four experiment reports `research/experiments/EXP-00N/report.md`, and `research/claims_register.csv`.
- **Performed by:** the AI assistant, by script and by hand; internal quality control, not external review. Journal entry J-0017; decision D-014.

## 1. Method

| Step | Tool | Output |
|---|---|---|
| Recompute headline numbers and counts from raw outputs (`results.json`, `metrics.csv`), independently of `paradox.analysis` | `scripts/m4_recompute_checks.py` | `results/audit/recompute_checks.json` |
| Trace every decimal number in the six documents to a committed source value at the stated precision | `scripts/m4_number_trace.py` | `results/audit/number_trace.json` |
| Map every figure, table and claim to experiment id, run ids, metric definition, result path and SHA-256, generator, config and protocol hashes and code revision; check that report figure copies are byte-identical to the generated files | `scripts/m4_build_manifest.py` | `research/publication/artifact_manifest.json` |
| Check external claims against sources actually opened | by hand, against `research/literature_review.md` | section 4 below |
| Check denominators, units, precision, uncertainty and sample counts | by hand, with the recomputation | section 3 below |

## 2. Results

| Check | Result |
|---|---|
| Raw-output recomputation | 31 of 31 checks pass (after the fix in section 2.1); includes the 32 rejected cells and their 20 MV / 12 SEQ split, the headline -0.1313 [-0.1350, -0.1276], P2 (9 disconfirmed, 21 supported), P3 (43, 2, 0), the between-seed SD range and median, CW in 120 of 120 cells, EXP-001 counts and max abs z, EXP-003 sign counts by model, EXP-004 per-seed identity with EXP-002 and 0 of 18 reversals |
| Number trace | 1153 decimal tokens in the six documents, 0 unmatched |
| Artifact manifest | 42 entries (18 figures and tables, 24 claims); every result path exists; every report figure copy is byte-identical to the generated file |
| Exit statuses | 0 for all four experiments; 0 failed, 0 dropped runs |

### 2.1 Mismatch found and fixed

| Where | Stated | Committed value | Fix |
|---|---|---|---|
| EXP-002 report section 8.1, CLM-002, journal J-0012 | the 32 rejected cells are 24 MV and 8 SEQ | 20 MV and 12 SEQ (`results/EXP-002/analysis/analysis.json` `rejected_cells`; recomputed from `metrics.csv`) | Report and CLM-002 corrected with a dated note; J-0012 left unchanged (append-only) and corrected by J-0017; D-014. No verdict depends on the split. |

### 2.2 Other findings fixed during M4

| Where | Finding | Fix |
|---|---|---|
| Manuscript draft v1 section 5.3 | "the Monte Carlo check agreed in sign with every exact value"; one of 183 intervals includes 0 | Corrected in the revision (review pass R14) |
| `research/experiment_registry.csv` | statuses ended "standalone report pending" although the reports exist | Updated |
| `research/limitations.md` | "Standalone reports pending" | Removed; M4 limitations added |
| `results/README.md` | "Empty at M0: no experiment has run" | Updated |
| `research/claims_register.csv` | statuses "audit pending (M4)"; columns lacked result ids, config hash, figure or table and section | Restructured with those columns; 14 rows added (3 exploratory, 2 descriptive, 1 diagnostic, 8 external) |

## 3. Denominators, units, precision, uncertainty and samples

- **Units.** Accuracy and `Delta` are proportions of items; budgets are calls per item; runtimes are seconds of wall-clock time. The manuscript states these units in captions and in section 3.
- **Denominators.** 240 is the primary family (MV and SEQ x 6 scenarios x 4 `lambda` x 5 budgets `B >= 3`); 30 P2 cells (6 scenarios x 5 budgets at `lambda = 0`); 45 P3 comparisons (3 scenarios x 5 budgets x 3 consecutive `lambda` steps); 120 CW cells with `B >= 3`; 432 non-baseline cells (3 rules x 6 budgets x 24 run cells); 48 matched EXP-003 cells and 183 run model cells (192 minus 9 inadmissible); 18 EXP-004 checks (3 cells x 5 levels plus 3 tie cells); 360 descriptive EXP-004 comparisons. All were recomputed or read from `analysis.json`.
- **Precision.** Simulated contrasts are given to 4 decimals (the SE is of order 0.001); exact closed-form values to 5 decimals; golden fixtures to the precision of the source. No value is given to more precision than its source file.
- **Uncertainty.** Every simulated contrast in the manuscript carries a seed-level t 95% interval, or is labelled as a point value from a table that does. Exact values carry none, by design. The P1 to P3 intervals are unadjusted, and the manuscript says so.
- **Samples.** 30 seed-runs of 2000 items per EXP-002 and EXP-004 cell; 30 seeds of 20,000 items per EXP-001 and EXP-003 cell; 10 exploratory seeds of 2000 items in the J-0016 sweep. Stated wherever these numbers are used.

## 4. External claims

| Key | What was opened (2026-11-24) | Claims that rely on it | Marked in the manuscript |
|---|---|---|---|
| chen2024 | arXiv abstract page | CLM-E01; sections 1, 2, 6 | "abstract read" |
| kaniovski2008 | working-paper PDF, pages 1 to 13 (SHA-256 in `references.bib`) | CLM-E02; Theorem 1 formula and fixtures in sections 2, 3, 5.1 | "full text pages 1 to 13 read" |
| kim2025 | arXiv abstract page | CLM-E03; sections 1, 2 | "abstract read" |
| golub2010 | AEA article page (abstract) | CLM-E04; sections 1, 2 | "abstract read" |
| mavrodiev2012 | arXiv abstract page | CLM-E05; sections 1, 2 | "abstract read" |
| wang2022 | arXiv abstract page | CLM-E06; sections 1, 2 | "abstract read" |
| li2024 | arXiv abstract page | CLM-E07; sections 1, 2 | "abstract read" |
| du2023 | arXiv abstract page | CLM-E08; section 2 | "abstract read" |

Boland (1989), Boland, Proschan and Tong (1989), Ladha (1992), Lorenz et al. (2011) and the other sources in `literature_review.md` section 2 were not opened. The manuscript does not cite them; it says that the common-shock model is attributed to Boland and co-authors in secondary sources that were not verified. The tertiary page `wiki-jury` was used only to locate sources and is not cited.

## 5. Strength and scope of evidence per conclusion

| Conclusion | Strength | Scope |
|---|---|---|
| Engine reproduces closed forms (CLM-001) | Strong within the grid | EXP-001 grid; cannot detect an error shared by model and formula |
| MV degrades in S4 and S6 (CLM-002 to CLM-004) | Strong, but analytic: confirmed, not discovered | Common-shock and mixture families; `B <= 31` |
| SEQ loses less than MV where MV degrades (CLM-005) | Strong for this rule | One SEQ rule; mechanism untested |
| Correlation reduces the MV gain in homogeneous scenarios (CLM-006) | Strong at `B <= 31` | Common-shock model; limit behaviour differs (CLM-011) |
| Sign depends on the dependence model (CLM-008, CLM-009) | Strong (exact values) | Four models, `n <= 15`; extended exploratorily (CLM-012) |
| No reversal under secondary choices (CLM-010) | Weak | 3 of 32 cells; 15 of 18 checks insensitive by construction |
| CW above SINGLE (CLM-007, CLM-013) | Not a finding about aggregation | Driven by the assumed confidence model |

## 6. Limits of this audit

- The number trace matches a token when some committed value rounds to it; one- and two-decimal tokens (mostly design parameters such as 0.95 or 0.4) can match by coincidence and were reviewed by hand. Tokens with three or more decimals were matched at their stated precision.
- Integer counts are covered by the recomputation script and by hand, not by the trace.
- EXP-004 recomputation uses `results/EXP-004/metrics.csv`, which is git-ignored (D-012); in a fresh clone those checks are reported as skipped until `scripts/m3_run.sh EXP-004` regenerates it.
- The audit was performed by the same AI system that drafted the documents. The owner's review is pending.
