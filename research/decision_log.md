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
