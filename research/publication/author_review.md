<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Owner review (checklist; not started)

Only the owner ticks these boxes. Recorded owner decisions, for reference (not ticks): the protocol freezes were approved on 2026-11-24 (`research/freeze.json`, D-009); the titles and the funding, competing-interest and AI-use statements were approved on 2026-11-25 ("Approve all", post-M4; D-015); the owner's answers of 2026-11-26 are recorded below (D-018). Full-text owner review of the manuscript is pending (M6). A box ticked by an AI session at the freeze was unticked in M5 (D-016).

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
3. The repository URL and the demo URL are owner-only facts and are still placeholders. (Settled 2026-11-26: filled, B1 and B2.)
4. "Funding: none" and "Competing interests: none declared" still need the owner's confirmation before any release. (Settled 2026-11-26: B4.)
5. The author line and the affiliation are owner-only facts; the current text follows decision C3 of 2026-11-24 and needs the owner's confirmation at sign-off. (Settled 2026-11-26: B3.)
6. No manuscript title other than the one approved on 2026-11-25 may be used; the owner decides whether `CITATION.cff` should carry that title (set in M6) or a software title. (Settled 2026-11-26: manuscript title, B7.)
7. `CITATION.cff` has no `date-released`; re-adding it belongs to the owner's publication step, and the version `0.1.0-rc1` should be changed to the release version at that step. (Settled 2026-11-26: B8, recorded in `release_checklist.md`.)
8. The articles (`articles/medium.md`, `articles/linkedin.md`) are drafts written by the AI system and have not been reviewed by the owner.
9. The owner decides whether to keep the closing sentence of manuscript section 11 about pending full-text review once the review is done.
10. The owner decides whether the reference to Chen et al. (2024) should keep the v1 title (current text, with the v2 title also given) or use the v2 title only. (Settled 2026-11-26: v2 title, R-PARADOX-1.)
11. Decisions D-002, D-006, D-007, D-008, D-010, D-011 and D-012 were taken by sessions and are recorded as "open to owner review" in `research/decision_log.md`; D-005 is a session decision without that note. (Settled 2026-11-26: accepted, R-PARADOX-1.)
12. `data/manifest.json` still says the synthetic generator is "planned (M2)"; it was left unchanged because its SHA-256 is quoted in the four `reproduction.md` files, so updating it is the owner's call. (Settled 2026-11-26: dated note in `data/README.md`, file unchanged, R-PARADOX-1.)
13. The release checklist items "Owner review checklist signed off" and "Owner approval for any push or publication" stay unticked until the owner acts.

### Remaining owner placeholders (as of the 2026-11-26 commit)

None. The eight placeholders listed at M6 (repository URL in `README.md`, `articles/linkedin.md`, `articles/medium.md` and manuscript section 10; demo URL in `README.md`, `demo/README.md` and `articles/linkedin.md`; funding and competing interests in manuscript section 11) were filled on 2026-11-26 from the owner's answers (D-018).

## Owner answers recorded (2026-11-26)

Authority: owner, 2026-11-26, decision sheet (`labs/_shared/owner-decision-sheet-2026-11-26.md` and `labs/_shared/owner-approvals-2026-11-26.md`, outside this repository); decision D-018. These are recorded answers, not ticks: no box above is ticked.

| Id | Answer | Applied here |
|---|---|---|
| A1 | Correct the out-of-date "not pushed" sentences. | `release_checklist.md` status, README status, articles README. The repository is public since 2026-11-25. |
| B1 | Repository URL `https://github.com/mohamedbechirkefi/paradox-reasoner-aggregation`. | README, articles, manuscript section 10, `CITATION.cff` `repository-code`. |
| B2 | Demo hosted on Cloudflare Workers (free plan) at `https://paradox-reasoner-aggregation.kefimohamedbechir.workers.dev`. | README, demo README, articles, manuscript section 10; `demo/wrangler.jsonc` (assets only, `./dist`). Deployed by the coordinator. |
| B3 | Author "Mohamed Bechir Kefi", independent researcher. | Manuscript, supplementary, four reports, `CITATION.cff` affiliation, README, demo footer. `pyproject.toml` has no authors field. The frozen protocols and `research/freeze.json` (C3) are not edited. |
| B4 | No funding; no competing interests. | Manuscript section 11; "to be confirmed" marks removed. |
| B6, B7 | Manuscript title approved; `CITATION.cff` carries it. | Already equal; comment updated. |
| B8 | `0.1.0-rc1` kept, no `date-released`; `0.1.0` and the release day at the release. | Recorded in `release_checklist.md`. |
| B9 | Scrub home paths from editable files; no history rewrite. | None were left in editable files since M6; what remains is listed in `reproducibility_report.md` section 7. |
| B10 | PDFs kept and attached to a release. | No change. |
| B11, B13 | Release-note sentences. | `release_checklist.md`, "Release notes (draft)". |
| B14 | Source labels accepted. | Recorded; no text change. |
| R-PARADOX-1 | Session decisions D-002, D-005 to D-008, D-010 to D-012 accepted; dated note outside `data/manifest.json`; Chen et al. (2024) cited by its v2 title. | D-018; `data/README.md`; manuscript, `references.bib`, `literature_review.md`. |

Still open (owner only):

- B15: the article drafts (`articles/medium.md`, `articles/linkedin.md`) and their titles, before any posting.
- B16: full-text review of the manuscript, supplementary appendix, reports, evidence audit and second review pass, then the sign-off of this checklist (open decisions 1, 8, 9 and 13 above).
- B18: the release, tag and any DOI or preprint.
- Freezes: none is pending in this repository (EXP-001 to EXP-004 are frozen); any new experiment needs its own freeze.
