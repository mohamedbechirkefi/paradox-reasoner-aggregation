<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Owner review (checklist; not started)

Only the owner ticks these boxes. Recorded owner decisions, for reference (not ticks): the protocol freezes were approved on 2026-11-24 (`research/freeze.json`, D-009); the titles and the funding, competing-interest and AI-use statements were approved on 2026-11-25 ("Approve all", post-M4; D-015). Full-text owner review of the manuscript is pending (M6). A box ticked by an AI session at the freeze was unticked in M5 (D-016).

Decisions reserved to the owner:

- [ ] Protocol freezes (EXP-001 to EXP-004), with version and hash: v1.0, owner-approved 2026-11-24, hashes in `research/freeze.json` and the registry.
- [ ] Authorship and affiliation metadata of the manuscript and reports.
- [ ] AI-assistance disclosure text.
- [ ] Final title and abstract.
- [ ] Every public claim in README, demo and articles.
- [ ] Any publication, push, release or preprint upload.

No box above is ticked. The M6 session (2026-11-25) found no box ticked by an agent and ticked none.

## Prepared for the owner (M6, 2026-11-25)

Authority for M6: owner, 2026-11-25, "Next" (second) (`labs/_shared/owner-approvals-2026-11-25e.md`, outside this repository). M6 prepared a release candidate; it released nothing.

### What to read for each box

| Box | What to read |
|---|---|
| Protocol freezes | `research/freeze.json` (hashes and the quoted approval); `research/experiment_registry.csv` (version and SHA-256 per experiment); manuscript section 4.1. |
| Authorship and affiliation metadata | Manuscript section "Author and affiliation metadata" (lines 8 to 13); the "Author" row of each experiment report, section 1; `CITATION.cff` (authors, title, version). |
| AI-assistance disclosure text | Manuscript section "Author and affiliation metadata" (AI assistance bullet) and section 11 (third bullet); the "Author" rows of the reports, section 1. |
| Final title and abstract | Manuscript title line and section "Abstract"; `CITATION.cff` title (set to the manuscript title in M6). |
| Every public claim in README, demo and articles | `README.md` (status, key results, limitations); `articles/medium.md`; `articles/linkedin.md`; the demo (`demo/`, build with `npm run build`, open `dist/`); `research/publication/claims_audit.md`, `research/publication/evidence_audit.md` and `research/publication/review_pass_2.md` for the evidence behind each claim. |
| Any publication, push, release or preprint upload | `research/publication/release_checklist.md`, `research/publication/reproducibility_report.md` (clean-clone record of M6), `research/publication/dependency_licences.md`, and the compiled PDFs: `research/paper/manuscript.pdf`, `research/paper/supplementary.pdf`, `research/experiments/EXP-00N/report.pdf`. |

### Open decisions for this repository

1. Full-text review of the manuscript, the supplementary appendix, the four experiment reports, the evidence audit and the second review pass is pending; only the titles and the section 11 statements were approved (D-015).
2. Any push, release, tag, licence change or publication of any kind is undecided (G-PUBLIC); M6 does not decide it.
3. The repository URL and the demo URL are owner-only facts and are still placeholders.
4. "Funding: none" and "Competing interests: none declared" still need the owner's confirmation before any release.
5. The author line and the affiliation are owner-only facts; the current text follows decision C3 of 2026-11-24 and needs the owner's confirmation at sign-off.
6. No manuscript title other than the one approved on 2026-11-25 may be used; the owner decides whether `CITATION.cff` should carry that title (set in M6) or a software title.
7. `CITATION.cff` has no `date-released`; re-adding it belongs to the owner's publication step, and the version `0.1.0-rc1` should be changed to the release version at that step.
8. The articles (`articles/medium.md`, `articles/linkedin.md`) are drafts written by the AI system and have not been reviewed by the owner.
9. The owner decides whether to keep the closing sentence of manuscript section 11 about pending full-text review once the review is done.
10. The owner decides whether the reference to Chen et al. (2024) should keep the v1 title (current text, with the v2 title also given) or use the v2 title only.
11. Decisions D-002, D-006, D-007, D-008, D-010, D-011 and D-012 were taken by sessions and are recorded as "open to owner review" in `research/decision_log.md`; D-005 is a session decision without that note.
12. `data/manifest.json` still says the synthetic generator is "planned (M2)"; it was left unchanged because its SHA-256 is quoted in the four `reproduction.md` files, so updating it is the owner's call.
13. The release checklist items "Owner review checklist signed off" and "Owner approval for any push or publication" stay unticked until the owner acts.

### Remaining owner placeholders (file and line, as of the M6 commit)

| File | Line | Placeholder |
|---|---|---|
| `README.md` | 8 | repository URL and demo URL |
| `demo/README.md` | 6 | demo URL |
| `articles/linkedin.md` | 12 | repository URL |
| `articles/linkedin.md` | 13 | demo URL |
| `articles/medium.md` | 44 | repository URL |
| `research/paper/manuscript.md` | 212 | repository URL (section 10) |
| `research/paper/manuscript.md` | 216 | funding, "to be confirmed by the owner before any release" |
| `research/paper/manuscript.md` | 217 | competing interests, "to be confirmed by the owner before any release" |
