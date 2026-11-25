<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Decision log

Append-only. Each entry: id, date, decision, decided by, context, alternatives, consequences.

## D-001: Licence is the owner's custom non-commercial licence, not a permissive licence

- **Date:** 2026-11-24
- **Decided by:** the owner
- **Context:** Master prompt section 2 asks for an "owner-approved permissive code license". On 2026-11-24 the owner instead chose the PARADOX Source-Available Non-Commercial Research License v1.0 (SPDX `LicenseRef-PARADOX-NC-Research-1.0`) for all original material, for their own protection, with a Contributor License Agreement.
- **Alternatives:** a permissive licence (MIT, Apache-2.0) as the prompt suggests.
- **Consequences:** the repository is source-available, not OSI open source; README and CITATION.cff must not describe it as open source. Licence files (`LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `CONTRIBUTING.md`, `.github/`) are the owner's and are not modified by sessions. Third-party data and dependencies keep their own licences, recorded in `data/manifest.json` and the lockfile. CITATION.cff names the licence in a comment, not as an SPDX `license` field, because the identifier is not on the SPDX list.

## D-002: Zero-cost publication toolchain is pandoc plus the typst Python package

- **Date:** 2026-11-24
- **Decided by:** session (M0), within the master prompt's zero-cost constraint; open to owner review
- **Context:** no TeX distribution is installed; installing one is not needed. pandoc 3.6.3 and typst 0.15.0 (Python package) are available locally.
- **Decision:** Markdown is canonical. PDFs: pandoc to Typst (`-V mainfont="Libertinus Serif"`, required, see feasibility section 3) and compile with `typst.compile`. `manuscript.tex` is generated with pandoc as a source deliverable and is not compiled locally.
- **Consequences:** no claim that a LaTeX-compiled PDF exists. Visual inspection of Typst PDFs is required at M6.

## D-003: Synthetic binary-choice reasoners with a common-shock correlation model as the primary model (proposal)

- **Date:** 2026-11-24
- **Decided by:** session proposal; requires owner approval at freeze
- **Context:** Master prompt section 10 defaults to deterministic synthetic reasoners with calibrated error and correlated mistakes.
- **Decision:** binary decisions; two-class difficulty mixture; opinion-leader (common-shock) correlation with parameter `lambda`; five rules (SINGLE, MV, CW, SEQ, DELIB); accuracy as the single primary metric; SINGLE as baseline. Alternatives (Bahadur, Beta difficulty) are used in the EXP-003 sensitivity analysis.
- **Alternatives considered:** K-ary answers (deferred; binary keeps exact theory available); Gaussian-copula correlation (no simple closed form); local open-weight LLMs (out of scope without a separate protocol).
- **Consequences:** exact theoretical baselines exist for MV, so EXP-001 can validate the engine; MV outcomes in EXP-002 are largely predictable from theory, which is stated as a risk.

## D-004: No external dataset in the primary design

- **Date:** 2026-11-24
- **Decided by:** session proposal; owner may override
- **Context:** the question can be answered within a synthetic model; external per-item LLM correctness data would add licence and provenance risk.
- **Decision:** all data are generated. Candidate external sources are recorded in `data/manifest.json` as not adopted.
- **Consequences:** no redistribution issue; the claims boundary is strictly synthetic.

## D-005: Dependency versions bounded by an exclude-newer date

- **Date:** 2026-11-24
- **Decided by:** session (M0)
- **Context:** dependencies must have been released at least two weeks before 2026-11-24.
- **Decision:** `pyproject.toml` sets `[tool.uv] exclude-newer = "2026-11-10T00:00:00Z"`, so the resolver cannot pick a release from the last two weeks.
- **Consequences:** reproducible resolution; see `progress.md` for the `uv lock` outcome.

## D-006: Packaged layout, uv_build backend and a `report` dependency group with typst

- **Date:** 2026-11-24
- **Decided by:** session (M2); open to owner review
- **Context:** M2 needs a `paradox` CLI entry point and PDF generation from inside the project environment.
- **Decision:** `pyproject.toml` switches to `package = true` with the `uv_build` backend (`>=0.9.0,<0.10.0`) and a `[project.scripts]` entry `paradox`. A `report` dependency group adds `typst` (resolved to 0.15.2, uploaded 2026-11-05, inside the `exclude-newer` bound of D-005); `default-groups = ["dev", "report"]`. pandoc stays external (shared `.tools/pandoc`, overridable with `PARADOX_PANDOC`).
- **Consequences:** `uv sync` installs everything needed for tests and PDFs; `uv.lock` changed accordingly.

## D-007: Guards for exploratory and confirmatory runs

- **Date:** 2026-11-24
- **Decided by:** session (M2), implementing G-FREEZE mechanically; open to owner review
- **Decision:** `paradox run` refuses a `confirmatory` config unless the registry row holds a 64-hex SHA-256 equal to the protocol file's hash, the protocol header no longer says DRAFT, and the seed entropy is the confirmatory value 20261124. Exploratory configs may not use entropy 20261124 (held-out seeds stay unseen) and must write under a path with an `exploratory` component.
- **Consequences:** no confirmatory output can be produced before the owner freezes; exploratory outputs are physically separated (`results/exploratory/`).

## D-008: Common random numbers across cells, not only within runs

- **Date:** 2026-11-24
- **Decided by:** session (M2); open to owner review
- **Context:** protocol section 2.6 requires common random numbers across rules and budgets within a run. It does not say whether different `(scenario, lambda)` cells share seeds.
- **Decision:** every cell uses the same seed list, and each random component (labels, difficulty, leader, adoption, private answers, signals, speaking order, herding, switching, ties) has its own child stream, so cells are matched by seed. Rules and budgets use prefixes of one 31-reasoner table.
- **Consequences:** comparisons across `lambda` and scenarios are also paired by seed. Cells are therefore not independent of one another; analyses that pool cells must account for this. The owner may prefer independent seeds per cell at freeze.

## D-009: Protocols frozen at v1.0 with six owner-approved amendments

- **Date:** 2026-11-24
- **Decided by:** the owner (G-FREEZE). Approval recorded in `labs/_shared/owner-approvals-2026-11-24.md` (outside this repository) and quoted in `research/freeze.json`.
- **Context:** M2 proposed amendments A-1 to A-5 and an exposure disclosure; the owner answered them.
- **Decision:** apply exactly the approved amendments and freeze `research/protocol.md` and EXP-001 to EXP-004 at v1.0: (1) 30 seeds per cell; (2) DELIB dropped from the primary analysis, the reason (identical to MV at half the calls) reported as a limitation; (3) EXP-004 stays optional; (4) inadmissible Bahadur cells reported as exclusions; (5) command names updated, seeds shared across cells (D-008 confirmed); (6) exploratory S1/S4 values disclosed. Common decisions C1 (synthetic data only), C2 (PDFs through pandoc and Typst), C3 (authorship: Mohamed Bechir Kefi, no affiliation, AI disclosed as a research and development assistant) and C4 (disclosure of exploratory primary values) apply.
- **Not applied:** A-3 (fix the confidence parameter from a stated target) was not among the approved amendments; the confidence model is unchanged and its influence on CW is a stated limitation.
- **Consequences:** the freeze record `research/freeze.json` holds the approval, C1 to C4, the C4 values and paths, and the SHA-256 of the main protocol, every experiment protocol and every confirmatory config, with the git revision `3b595680e8e36e01e0a3f9abdf80632929fc1475`. Registry statuses are "frozen (owner-approved 2026-11-24), not yet run". Any later change to a frozen file is a dated post-freeze deviation.

## D-010: EXP-004 implementation and a stricter freeze guard

- **Date:** 2026-11-24
- **Decided by:** session (freeze), implementing the frozen protocol; open to owner review
- **Decision:** (a) the EXP-004 tie level "abstain counted as wrong" is implemented as `tie_rule = "abstain_wrong"` for MV and SEQ (default `"coin"`); (b) an aggregation config may carry `variants`, each overriding only `budgets`, `rules`, `tie_rule`, `w` or `tau`, so EXP-004 is one config with eight one-factor variants; the cost factor is computed from `messages_per_item` of the primary variant; (c) `paradox run` now also requires `research/freeze.json` to list the experiment with the same protocol hash, the current hash of `research/protocol.md`, and the hash of the exact config (canonical JSON, plus file bytes when read from a file).
- **Consequences:** a changed confirmatory config, a changed protocol or a missing freeze record is refused (exit code 3). Tests cover acceptance of the four frozen configs and refusal of changed ones. The metrics CSV of aggregation runs gains a `variant` column (empty when no variants).

## D-011: Operational readings of the frozen analysis, fixed before any confirmatory output

- **Date:** 2026-11-25
- **Decided by:** session (M3), before any confirmatory run; open to owner review. No protocol, config, seed or exclusion rule changes.
- **Context:** the frozen protocol states the decision rules in words. The runner computes the seed-level summaries and the Holm adjustment, but nothing applied P1 to P3, the EXP-003 sign rule or the EXP-004 reversal rule. Writing that code after seeing results would allow analysis choices to follow the data.
- **Decision:** `src/paradox/analysis.py` (tests in `tests/test_analysis.py`) was written, tested on exploratory documents and committed before any confirmatory run, with these readings: (a) EXP-002 H0 is rejected in a cell when the Holm-adjusted one-sided p-value is below 0.05; at Holm step `k` this is the same as the one-sided upper bound at level `0.05 / (m - k)` lying below 0, which is also reported; (b) the "lower bound" and "upper bound" of P1 to P3 are the seed-level two-sided t 95% intervals of protocol section 5, unadjusted; P2 uses the per-seed paired difference `Delta_SEQ - Delta_MV`; P3 compares consecutive `lambda` levels at fixed `B >= 3` with per-seed paired differences; (c) EXP-003 sign agreement is judged on the exact analytic values, which exist for all four models, with Monte Carlo intervals as a check; (d) EXP-004 "significant (Holm)" cells are EXP-002 primary-family cells with Holm-adjusted p below 0.05 (significant degradation, since the family is one-sided); a sign is reversed when the variant's t 95% interval for the same cell lies above 0; for the tie factor, whose even budgets do not exist in EXP-002, the reference is the primary tie level `tie_coin` with its own Holm family.
- **Consequences:** reading (d) for the tie factor, and the choice of consecutive steps in (b), are interpretations the protocol does not spell out; the reports say so. Anything else computed is labelled descriptive or exploratory.

## D-012: M3 storage of raw results, and standalone reports left for a later session

- **Date:** 2026-11-25
- **Decided by:** session (M3), following the M3 brief and the coordinator's instruction; open to owner review.
- **Context:** the M3 brief commits raw results when an experiment's outputs total less than 20 MB. `results/EXP-004/` totals 22 MB (`results.json` 13.1 MB, `metrics.csv` 3.6 MB). Separately, the session's file tool refused to write the section 11.3 experiment reports (`research/experiments/EXP-NNN/report.md`), and the coordinator instructed that such reports be left unwritten rather than produced by another route.
- **Decision:** (a) `results/EXP-001/` to `results/EXP-003/` are committed in full; for `results/EXP-004/`, `results.json` and `metrics.csv` are git-ignored, and the SHA-256 manifest, provenance table, run manifest, analysis outputs, generated report and figures are committed. (b) The four standalone 11.3 reports are not written in this session. The frozen-rule analyses (`results/EXP-00N/analysis/analysis.md` and `analysis.json`), the generated run reports (`results/EXP-00N/report.md` and `report.pdf`), the journal (J-0009 to J-0014) and the claims register (CLM-001 to CLM-010) hold the results.
- **Consequences:** the M3 acceptance criterion "per-experiment report drafts" and the publication gate are not yet met; a later session must write the four reports from the committed analysis outputs. EXP-004 raw files are regenerated with `scripts/m3_run.sh EXP-004` (after moving the existing folder aside) and checked against `results/EXP-004/sha256_manifest.json`; timing fields differ between reruns, so `results.json` hashes match only for the record content.

## D-013: The owner approves writing the missing experiment reports from committed results

- **Date:** 2026-11-25
- **Decided by:** the owner: owner, 2026-11-25, "approve all recommendations, RIGGED A" (recorded in `labs/_shared/owner-approvals-2026-11-25.md`, outside this repository, item 4 "Experiment reports").
- **Decision (item 4, as recorded):** "The owner approves writing the missing 11.3/11.6 experiment reports (`report.md`, and `reproduction.md` where the repo uses it). They are written from the committed results, tables and figures only." "Nothing is recomputed and no numbers change." The other items of that record concern other projects.
- **Consequences:** this supersedes part (b) of D-012 in principle. In the M3 close session (2026-11-25) the file tool again refused to write `research/experiments/EXP-001/report.md`. As the close brief requires, writing stopped there and no other route was used. Following the coordinator's report-return note, the session composed `report.md` and `reproduction.md` for EXP-001 to EXP-004 from committed results only and returned them as text; the coordinator writes and commits the files. No protocol, config, seed, exclusion rule, analysis code or result changed. The freeze record is not touched: no deviation from the frozen protocols arose. Part (a) of D-012 (EXP-004 raw files git-ignored) stands.

## D-014: M4 interpretation: exploratory sensitivity checks, audit corrections and manuscript revision

- **Date:** 2026-11-25
- **Decided by:** session (M4), under the owner's instruction: owner, 2026-11-25, "Approve all recommendations, push then next" (`labs/_shared/owner-approvals-2026-11-25b.md`, item 5: M4 for each project that has finished M3; no item of that record is specific to PARADOX). Open to owner review.
- **Context:** M4 requires confounder inspection, an evidence audit and a manuscript. The EXP-002 protocol names competing explanations (below-chance mass, correlation, herding, finite budget, the confidence model behind CW) that the confirmatory results address only in part. The audit found that the EXP-002 report, CLM-002 and J-0012 gave the 32 rejected cells as 24 MV and 8 SEQ, while `analysis.json` and the raw outputs give 20 MV and 12 SEQ.
- **Decision:** (a) Three cheap exploratory checks were made after all verdicts and labelled as such: closed-form values at larger group sizes for the EXP-002 scenarios and the EXP-003 models (J-0015, `results/exploratory/m4-analytic/`), and a CW confidence-informativeness sweep with exploratory seeds (J-0016, `results/exploratory/m4-cw-delta/`, configs in `configs/exploratory/m4_cw_delta_*.json`). They change no frozen verdict and are reported beside the verdicts. (b) The split is corrected in the EXP-002 report (dated note) and CLM-002; J-0012 stays as written and J-0017 records the correction. (c) The claims register gains the columns result ids, config hash, figure or table and manuscript section, plus exploratory, descriptive and external rows. (d) The manuscript was drafted (v1, `7b9b696`), challenged in `research/publication/review_pass_2.md`, and revised where the challenge held (R1 to R14, R20). (e) Labelled addenda (section 9.1) were added to the EXP-002 and EXP-003 reports.
- **Consequences:** no protocol, config, seed, exclusion rule, analysis code or confirmatory result changed; no confirmatory run was made. The EXP-002 interpretation is now explicitly bounded to `B <= 31` where correlation is involved, CW is reported as assumption-driven, and the MV degradation is presented as analytic and confirmed rather than discovered.
