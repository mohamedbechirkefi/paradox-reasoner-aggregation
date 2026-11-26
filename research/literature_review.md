<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Literature review (M0 scoping pass)

**Scope and method.** A targeted, non-systematic search on 2026-11-24 with web search and page fetches. It is not a systematic review and supports no novelty claim. A source is listed as **verified** only if a page or PDF for it was actually opened in this session; what was verified is stated (abstract page, full text, metadata only). Everything else is **unverified** and must not be cited as read.

## 1. Verified sources (opened on 2026-11-24)

| Key | Reference | What was opened | Relevance |
|---|---|---|---|
| chen2024 | L. Chen, J. Q. Davis, B. Hanin, P. Bailis, I. Stoica, M. Zaharia, J. Zou. "Are More LM Calls All You Need? Towards the Scaling Properties of Compound AI Systems." arXiv:2403.02419 (v1 4 Mar 2024, titled "Are More LLM Calls All You Need? Towards Scaling Laws of Compound Inference Systems"; v2 4 Jun 2024, whose title is cited by owner decision of 2026-11-26, D-018). https://arxiv.org/abs/2403.02419 | arXiv abstract page | Reports that Vote and Filter-Vote performance can first increase and then decrease with the number of LLM calls, attributed to diversity of query difficulty. Motivates the two-class difficulty mixture. |
| kim2025 | E. Kim, A. Garg, K. Peng, N. Garg. "Correlated Errors in Large Language Models." arXiv:2506.07962 (9 Jun 2025); ICML 2025 per the arXiv page. https://arxiv.org/abs/2506.07962 | arXiv abstract page | Over 350 LLMs; substantial error correlation (models agree 60% of the time when both are wrong on one leaderboard dataset). Motivates the correlation axis. |
| wang2022 | X. Wang, J. Wei, D. Schuurmans, Q. Le, E. Chi, S. Narang, A. Chowdhery, D. Zhou. "Self-Consistency Improves Chain of Thought Reasoning in Language Models." arXiv:2203.11171 (v1 21 Mar 2022, v4 7 Mar 2023); ICLR 2023 per the arXiv page. https://arxiv.org/abs/2203.11171 | arXiv abstract page | Majority vote over sampled reasoning paths; the canonical LLM case of independent-sample voting. |
| li2024 | J. Li, Q. Zhang, Y. Yu, Q. Fu, D. Ye. "More Agents Is All You Need." arXiv:2402.05120 (v1 3 Feb 2024, v2 11 Oct 2024); TMLR per the arXiv page. https://arxiv.org/abs/2402.05120 | arXiv abstract page | Sampling-and-voting improves with more agents; the gain depends on task difficulty. Counterpoint to chen2024. |
| du2023 | Y. Du, S. Li, A. Torralba, J. B. Tenenbaum, I. Mordatch. "Improving Factuality and Reasoning in Language Models through Multiagent Debate." arXiv:2305.14325 (23 May 2023). https://arxiv.org/abs/2305.14325 | arXiv abstract page | Multi-round debate as an information-sharing rule; motivates DELIB. |
| kaniovski2008 | S. Kaniovski. "Aggregation of Correlated Votes and Condorcet's Jury Theorem." Working paper dated 11 September 2008, https://Serguei.Kaniovski.wifo.ac.at/fileadmin/pdf/condorcet.pdf, SHA-256 `371a81023bf0e6281dfcfea62d522b8e711671729ccf4382c9d55fcd029670b0` (24 pages; not stored in the repository) | full text, pages 1 to 13 read; Theorem 1 formula transcribed | Homogeneous juries with pairwise correlation; positive correlation lowers jury competence; enlargement can be detrimental up to a size. Source of the Bahadur closed form and golden fixtures. The published version (Theory and Decision, DOI 10.1007/s11238-008-9120-4) was not opened: the publisher page redirected to a login. Cite the working paper. |
| golub2010 | B. Golub, M. O. Jackson. "Naive Learning in Social Networks and the Wisdom of Crowds." American Economic Journal: Microeconomics 2(1): 112-49, 2010. DOI 10.1257/mic.2.1.112 | AEA article page (abstract) | Repeated averaging converges to the truth only if the most influential agent's influence vanishes. Motivates information-sharing degradation. |
| mavrodiev2012 | P. Mavrodiev, C. J. Tessone, F. Schweitzer. "Effects of Social Influence on the Wisdom of Crowds." arXiv:1204.3463 (16 Apr 2012), Collective Intelligence 2012. https://arxiv.org/abs/1204.3463 | arXiv abstract page | Whether social influence helps depends on initial diversity and accuracy. |
| wiki-jury | Wikipedia contributors. "Jury theorem." https://en.wikipedia.org/wiki/Jury_theorem | page (tertiary source) | Used only to locate primary sources and the Kaniovski and Zaigraev numeric example (0.54505 at n = 3, 0.5196194 at n = 5 for p = 0.55, c = 0.4), which this project recomputed from kaniovski2008 Theorem 1. Not to be cited as evidence in the manuscript. |

## 2. Unverified sources (not opened; do not cite as read)

| Reference (as given by secondary sources) | Why unverified | Role |
|---|---|---|
| K. K. Ladha (1992). "The Condorcet Jury Theorem, Free Speech, and Correlated Votes." American Journal of Political Science 36(3): 617-634. DOI 10.2307/2111584 | only bibliographic listings seen | correlated-votes jury theorem |
| P. J. Boland (1989). "Majority Systems and the Condorcet Jury Theorem." The Statistician 38(3): 181-189. DOI 10.2307/2348873 | only secondary descriptions | opinion-leader dependence (basis of the common-shock model) |
| P. J. Boland, F. Proschan, Y. L. Tong (1989). "Modelling dependence in simple and indirect majority systems." Journal of Applied Probability 26(1): 81-88. DOI 10.2307/3214318 | listed by wiki-jury only | opinion-leader model |
| J. Lorenz, H. Rauhut, F. Schweitzer, D. Helbing (2011). "How social influence can undermine the wisdom of crowd effect." PNAS 108(22): 9020-9025. DOI 10.1073/pnas.1008636108 | PNAS returned 403; PMC and PubMed showed a browser check | social influence reduces diversity |
| L. Hong, S. E. Page (2004). "Groups of diverse problem solvers can outperform groups of high-ability problem solvers." PNAS 101(46): 16385-16389. DOI 10.1073/pnas.0403723101 | PubMed showed a cookie wall | diversity versus ability (contested) |
| S. Kaniovski, A. Zaigraev (2011). "Optimal Jury Design for Homogeneous Juries with Correlated Votes." Theory and Decision 71(4): 439-459. DOI 10.1007/s11238-009-9170-2 | listed by wiki-jury only | correlated juries |
| F. Dietrich, K. Spiekermann (2013). "Epistemic democracy with defensible premises." Economics and Philosophy 29(1): 87-120 | listed only | conditional independence |
| M. H. DeGroot (1974). "Reaching a Consensus." Journal of the American Statistical Association 69(345): 118-121 | not searched for directly | averaging dynamics |
| Optimal weighted voting (Nitzan and Paroush) and information cascades (Bikhchandani, Hirshleifer and Welch) | not searched in this session | CW rule rationale; SEQ rationale |

M1 must open the Boland and Ladha papers (or record them as permanently unverified) before the manuscript relies on them.

## 3. Known work and narrow contribution (draft)

Known: under independence and competence above one half, majority accuracy grows with group size (Condorcet); correlation and heterogeneity weaken or reverse this (Ladha, Boland, Kaniovski); LLM voting can be non-monotonic in the number of calls (chen2024) and LLM errors are correlated (kim2025); information sharing can help or hurt (golub2010, mavrodiev2012).

Proposed narrow contribution (not a novelty claim): a single reproducible engine that compares single-reasoner, independent-voting and information-sharing rules **at matched call budgets**, separates difficulty heterogeneity from conditional correlation, validates against exact closed forms, and tests whether pairwise correlation is a sufficient summary of the dependence (EXP-003). Whether this combination is new has not been established.

## 4. M6 full-text check (2026-11-25)

For each cited source that a manuscript or report claim depends on and that had been opened at abstract level only, a free, legal full text was opened on 2026-11-25 (arXiv PDF, or the authors' version on the second author's web page for golub2010). The cited claim was checked at the place stated below. The sources were not read cover to cover; only the cited claim was checked. The PDFs were not committed; their SHA-256 values are recorded here.

| Key | Full text opened | Pages | SHA-256 of the PDF | Claim checked at | Result |
|---|---|---|---|---|---|
| chen2024 | arXiv:2403.02419v2 (4 Jun 2024) | 18 | `73d7d364c09484816ca4e94e4f067c54aeba5f445583fdd26e96ec0d2fe586d5` | abstract, section 1, section 4.1 (Theorem 2) | Supported: Vote and Filter-Vote "can first increase but then decrease" with the number of calls; the non-monotonicity is attributed to "the diversity of query difficulties". The v2 title is "Are More LM Calls All You Need? Towards the Scaling Properties of Compound AI Systems"; the manuscript keeps the v1 title and now names both. |
| kim2025 | arXiv:2506.07962v1 | 29 | `12b4d40ebd8a7118c3ffd2fe7a458e0bedaef26df67d42486b9bfc32a31a1604` | abstract | Supported: "substantial correlation in model errors" over more than 350 LLMs. |
| wang2022 | arXiv:2203.11171v1 | 15 | `ed1ef6f3ff521a53b9cb873e8fad7991984a5c747ca0ae92d83d4e01e4f39326` | abstract, Figure 1 | Supported: sample a diverse set of reasoning paths and return the most consistent answer (majority vote in Figure 1). |
| li2024 | arXiv:2402.05120v2 (11 Oct 2024) | 18 | `d948be6a6068835cffe9b6f8b799861e188eea3a0204a90eec70e5faae0cfe57` | abstract, section 6 (Table 6) | Supported: performance "scales with the number of agents"; the gain is "correlated to the task difficulty". |
| du2023 | arXiv:2305.14325v1 | 27 | `b302ff15202dc3cda03f40ea1ac92b29e1519978540b345af92991f6d3e619b4` | abstract | Supported: several model instances debate over multiple rounds to reach a common answer. |
| golub2010 | authors' version (web.stanford.edu, page of M. O. Jackson) | 39 | `c9e0dd62b04a28617554ca29b3a97ccde7820f70e8e8efac873f479b8b14f4db` | abstract, section III | Supported: convergence to the truth holds "if and only if" the influence of the most influential agent vanishes as the society grows. The page numbers of the journal version were not checked. |
| mavrodiev2012 | arXiv:1204.3463v1 (Proceedings, CI 2012) | 7 | `9a3ee3bbe8e24e4984ed1d380a5eddaa042f4626ee7ac4d00efb4d35784ef079` | abstract | Supported: "the starting configuration of the population, in terms of its diversity and accuracy" determines how beneficial social influence is. |

kaniovski2008 was already read in full (pages 1 to 13). No cited claim needed qualification after the check. The sources in section 2 remain unverified and uncited.
