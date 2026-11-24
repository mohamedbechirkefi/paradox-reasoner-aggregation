<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Contributing to PARADOX

PARADOX is an independent, source-available research project maintained by Mohamed Bechir Kefi: collective reasoning.

Technical suggestions, bug reports, reproducibility results, corrections and Pull Requests are welcome. The project is available for non-commercial research under the PARADOX Source-Available Non-Commercial Research License v1.0 ([LICENSE](LICENSE)); it is not OSI-approved open-source software.

## 1. Before you start

For major changes, open an Issue first. Read `master_prompt.md`, `research/protocol.md` and `research/claims_register.csv`: frozen protocols are never changed silently, and every reported number must trace to a result file.

## 2. Pull Request requirements

- Your contribution is original or appropriately licensed, and you have the right to submit it.
- No credentials, secrets, confidential information or personal data.
- Relevant tests are included and pass; you report what you actually ran.
- Third-party dependencies and data sources are identified with their licenses.
- New files carry the header `SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0` where the format allows.
- You accept the Contributor License Agreement before your contribution is merged.

## 3. Contributor License Agreement

A recorded acceptance of [CLA.md](CLA.md) is required before merging copyrightable contributions. When you open a Pull Request, the "CLA Assistant" check comments on it; read the CLA, then post this exact comment:

    I have read the PARADOX CLA v1.0 and I hereby sign it

The check records your public GitHub username and account ID, the date and the PR. You sign once. If the check does not update, comment `recheck`. Checking a box is not a signature; the comment is.

The CLA lets the maintainer use, modify, distribute, relicense and commercially exploit accepted contributions. You keep the copyright in your original contributions.

## 4. Governance

Mohamed Bechir Kefi is the project owner and lead maintainer, and the only person who can change the protected `main` branch. The maintainer decides the research direction, protocol freezes, claims, releases and licensing.

## 5. Privacy and disclosure

Never commit an e-mail address, a name or any other personal identifier in code, logs, fixtures or results. Report security issues privately through GitHub's private vulnerability reporting.

## 6. Development commands

Environment (locked dependencies, Python 3.12):

    uv sync --frozen

Regenerate the lockfile (resolution is bounded by `exclude-newer` in `pyproject.toml`):

    uv lock

Test, smoke, run and report (M2):

    uv run paradox test
    uv run paradox smoke --pdf
    uv run paradox run --config configs/exploratory/probe_engine_validation.json --out results/exploratory/probe-engine-validation --pdf
    uv run paradox report results/exploratory/smoke --pdf

`paradox run` refuses a config labelled `confirmatory` unless the experiment's protocol is frozen (registry SHA-256 matching the protocol file, no DRAFT marker) and the config, the protocol and `research/protocol.md` match the hashes in `research/freeze.json`, and refuses exploratory output paths without an `exploratory` component. PDFs need pandoc (`PARADOX_PANDOC`, default the shared `.tools/pandoc`).
