<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Release checklist

**Status (2026-11-25, M6):** release candidate prepared, awaiting owner review and G-PUBLIC. The ticks below were verified in the M6 session; evidence is given for each. Nothing has been pushed, tagged or published.

- [x] Every registered experiment has a truthful standalone report (including failed or null ones). Evidence: `research/experiments/EXP-001/report.md` to `EXP-004/report.md` exist with PDFs; EXP-004 (H0 retained) and the disconfirmed P2 are reported; `research/experiment_registry.csv` lists 4 experiments.
- [x] Integrated manuscript complete; PDFs compiled and visually inspected (Typst path, decision D-002). Evidence: `scripts/m6_build_pdfs.py`; manuscript 10 pages, supplementary 6, reports 4, 8, 5 and 7 pages; every manuscript and supplementary page and the first and figure pages of each report inspected as PNG (`reproducibility_report.md` section 2).
- [x] Claims audit complete. Evidence: `claims_audit.md` (24 rows); `scripts/m4_recompute_checks.py` 31 checks, 0 failed; `scripts/m4_number_trace.py` 1153 tokens, 0 unmatched; external sources checked in full text (`evidence_audit.md` section 7).
- [x] Reproducibility report complete with actual outputs. Evidence: `reproducibility_report.md` (clean clone of `51bd9fc`: 327 tests passed, smoke reproduced, `A11Y-CHECK PASS`, exports deterministic).
- [x] Artifact manifest maps every figure, table and number. Evidence: `artifact_manifest.json` 42 entries; 28 paths present and tracked; 18 of 18 hashes match.
- [x] README status, experiment table and limitations current. Evidence: README read in M6; `tests/test_demo_export.py` passes (README decimals traced); `scripts/m6_check_links.py` 61 relative links, 0 broken.
- [x] Licence files unchanged; third-party licences recorded. Evidence: `git diff` shows no change to `LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`; `dependency_licences.md` (MPL-2.0 flags only).
- [x] No secrets, e-mail addresses or personal identifiers in committed files. Evidence: scan of `git ls-files` (`reproducibility_report.md` section 4): 0 keys, 0 `.env`, 1 non-personal service address (commit trailer); home-directory paths removed from current files, kept in append-only records and committed run logs. The author's name appears by owner decision C3.
- [ ] Owner review checklist signed off.
- [ ] Owner approval for any push or publication (G-PUBLIC).
