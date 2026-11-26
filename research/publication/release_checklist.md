<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Release checklist

**Status (2026-11-25, M6):** release candidate prepared, awaiting owner review and G-PUBLIC. The ticks below were verified in the M6 session; evidence is given for each.

**Update (2026-11-26):** the repository was pushed to <https://github.com/mohamedbechirkefi/paradox-reasoner-aggregation> on 2026-11-25 and is public since then, together with everything committed in it. No tag, release, DOI or preprint exists. The owner's answers of 2026-11-26 (owner, 2026-11-26, decision sheet; D-018) were applied as wording and configuration changes; no result changed.

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

## Version and date at the release (B8, owner, 2026-11-26)

`CITATION.cff` keeps `version: 0.1.0-rc1` and no `date-released` until the release. At the release, the version becomes `0.1.0` and `date-released` is set to the release day. `pyproject.toml` stays at `0.0.0`, because changing it would change the lockfile and the recorded environments.

## Release notes (draft)

- Figures: no figure of this repository is on the owner's list of figures with small or clipped labels (B11); the 24-panel EXP-002 figure is dense at page size and legible when zoomed (`reproducibility_report.md` section 2), and it is kept as a checksummed result.
- External build and check tools are used but not redistributed: pandoc (GPL-2.0-or-later) for the PDFs, Google Chrome (headless) for the demo accessibility check, the fonts bundled with Typst and embedded in the PDFs (SIL Open Font License 1.1 and the DejaVu licence), and the MPL-2.0 packages `lightningcss` (demo build) and `hypothesis` (tests), as listed in `dependency_licences.md`.
- The demo is hosted as Cloudflare Workers static assets on the free plan at <https://paradox-reasoner-aggregation.kefimohamedbechir.workers.dev> (`demo/wrangler.jsonc`, assets only), deployed by the coordinator.
