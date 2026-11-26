<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Supplementary appendix to "When more reasoners make worse decisions"

Author: Mohamed Bechir Kefi, independent researcher.

**Status: independent research manuscript / preprint draft, not peer-reviewed.** Every table below is copied from a generated, committed file named in its caption; the mapping is in `research/publication/artifact_manifest.json`.

## S1. Experimental matrix, hashes and runs

All four protocols are v1.0, frozen by the owner on 2026-11-24 (`research/freeze.json`; frozen files at commit `3b59568`, freeze record at `af85039`). Main protocol SHA-256: `68ce4b150fc8350b66a2e89d6c9049e241555a05bb7e381243b42a7dd5654de9`. All confirmatory runs used code revision `d997cf81784aaf136e385e489febaade7e18e55c` and confirmatory seed entropy 20261124 (30 seeds, shared across cells, D-008).

| Experiment | Protocol SHA-256 (prefix) | Config canonical SHA-256 (prefix) | Run ids | Units | Excluded | Failed | Exit | Verdict (frozen rule) |
|---|---|---|---|---|---|---|---|---|
| EXP-001 | `3e5f7992` | `ec431b20` | CELL-0001 to CELL-0312 | 292 cells run, 30 seeds x 20,000 items each | 20 (inadmissible Bahadur, listed in the protocol) | 0 | 0 | PASS |
| EXP-002 | `93a7b675` | `a69b5eb8` | RUN-0001 to RUN-0720 | 720 runs of 2000 items | 0 | 0 | 0 | H0 rejected (32 of 240 cells) |
| EXP-003 | `8e59d02e` | `70d5474b` | CELL-0001 to CELL-0192 | 183 model cells run, exact values plus 30 seeds x 20,000 items | 9 (inadmissible Bahadur, listed in the protocol) | 0 | 0 | H0 rejected (16 of 48 matched cells) |
| EXP-004 (optional) | `55c261f9` | `9f7e8cbf` | RUN-0001 to RUN-1440 | 1440 runs of 2000 items | 0 | 0 | 0 | H0 retained (0 of 18 checks reversed) |

Full hashes are in `research/freeze.json` and `research/experiment_registry.csv`; per-run provenance in `results/EXP-00N/provenance.csv`; per-file SHA-256 in `results/EXP-00N/sha256_manifest.json`.

## S2. EXP-002: all Holm-rejected cells and the P2 contrasts

Table S2a. The 32 cells with Holm-adjusted one-sided p below 0.05 (20 MV, 12 SEQ). Delta is the mean over 30 seed-runs; t95 is the unadjusted seed-level interval. Source: `results/EXP-002/analysis/analysis.json` (`rejected_cells`); Holm-adjusted p-values and step bounds are in `results/EXP-002/analysis/analysis.md`.

| Scenario | lambda | Rule | B | Delta | t95 |
|---|---|---|---|---|---|
| S4 | 0 | MV | 9 | -0.0213 | [-0.0246, -0.0180] |
| S4 | 0 | MV | 15 | -0.0403 | [-0.0434, -0.0372] |
| S4 | 0 | MV | 31 | -0.0570 | [-0.0602, -0.0537] |
| S4 | 0.25 | MV | 9 | -0.0074 | [-0.0107, -0.0042] |
| S4 | 0.25 | MV | 15 | -0.0107 | [-0.0142, -0.0072] |
| S4 | 0.25 | MV | 31 | -0.0150 | [-0.0185, -0.0116] |
| S6 | 0 | MV | 3 | -0.0153 | [-0.0182, -0.0123] |
| S6 | 0 | MV | 5 | -0.0340 | [-0.0374, -0.0307] |
| S6 | 0 | MV | 9 | -0.0658 | [-0.0695, -0.0621] |
| S6 | 0 | MV | 15 | -0.0955 | [-0.0995, -0.0915] |
| S6 | 0 | MV | 31 | -0.1313 | [-0.1350, -0.1276] |
| S6 | 0 | SEQ | 3 | -0.0087 | [-0.0115, -0.0059] |
| S6 | 0 | SEQ | 5 | -0.0132 | [-0.0171, -0.0092] |
| S6 | 0 | SEQ | 9 | -0.0182 | [-0.0222, -0.0143] |
| S6 | 0 | SEQ | 15 | -0.0247 | [-0.0291, -0.0202] |
| S6 | 0 | SEQ | 31 | -0.0266 | [-0.0316, -0.0216] |
| S6 | 0.25 | MV | 3 | -0.0118 | [-0.0150, -0.0085] |
| S6 | 0.25 | MV | 5 | -0.0255 | [-0.0286, -0.0224] |
| S6 | 0.25 | MV | 9 | -0.0411 | [-0.0454, -0.0369] |
| S6 | 0.25 | MV | 15 | -0.0487 | [-0.0531, -0.0443] |
| S6 | 0.25 | MV | 31 | -0.0527 | [-0.0571, -0.0483] |
| S6 | 0.25 | SEQ | 3 | -0.0064 | [-0.0093, -0.0034] |
| S6 | 0.25 | SEQ | 5 | -0.0107 | [-0.0146, -0.0068] |
| S6 | 0.25 | SEQ | 9 | -0.0139 | [-0.0180, -0.0097] |
| S6 | 0.25 | SEQ | 15 | -0.0178 | [-0.0222, -0.0134] |
| S6 | 0.25 | SEQ | 31 | -0.0203 | [-0.0246, -0.0159] |
| S6 | 0.5 | MV | 3 | -0.0074 | [-0.0102, -0.0047] |
| S6 | 0.5 | MV | 5 | -0.0111 | [-0.0139, -0.0082] |
| S6 | 0.5 | MV | 9 | -0.0103 | [-0.0133, -0.0072] |
| S6 | 0.5 | SEQ | 9 | -0.0068 | [-0.0103, -0.0034] |
| S6 | 0.5 | SEQ | 31 | -0.0102 | [-0.0134, -0.0069] |
| S6 | 0.75 | MV | 3 | -0.0036 | [-0.0054, -0.0018] |

Table S2b. P2 at `lambda = 0`: per-seed paired `Delta_SEQ - Delta_MV`, mean and t95. "Disconfirmed" means the interval lies above 0. Source: `results/EXP-002/analysis/analysis.json` (`P2.cells`).

| Scenario | B | SEQ minus MV | t95 | Status |
|---|---|---|---|---|
| S1 | 3 | -0.0239 | [-0.0264, -0.0213] | supported |
| S1 | 5 | -0.0468 | [-0.0508, -0.0428] | supported |
| S1 | 9 | -0.0806 | [-0.0848, -0.0764] | supported |
| S1 | 15 | -0.1287 | [-0.1330, -0.1245] | supported |
| S1 | 31 | -0.2084 | [-0.2125, -0.2043] | supported |
| S2 | 3 | -0.0123 | [-0.0146, -0.0099] | supported |
| S2 | 5 | -0.0248 | [-0.0290, -0.0206] | supported |
| S2 | 9 | -0.0403 | [-0.0447, -0.0359] | supported |
| S2 | 15 | -0.0729 | [-0.0781, -0.0676] | supported |
| S2 | 31 | -0.1309 | [-0.1364, -0.1253] | supported |
| S3 | 3 | -0.0468 | [-0.0494, -0.0442] | supported |
| S3 | 5 | -0.0732 | [-0.0767, -0.0698] | supported |
| S3 | 9 | -0.0908 | [-0.0938, -0.0878] | supported |
| S3 | 15 | -0.0971 | [-0.0998, -0.0944] | supported |
| S3 | 31 | -0.0928 | [-0.0949, -0.0907] | supported |
| S4 | 3 | -0.0036 | [-0.0059, -0.0014] | supported |
| S4 | 5 | +0.0035 | [+0.0003, +0.0066] | disconfirmed |
| S4 | 9 | +0.0241 | [+0.0214, +0.0268] | disconfirmed |
| S4 | 15 | +0.0408 | [+0.0380, +0.0437] | disconfirmed |
| S4 | 31 | +0.0572 | [+0.0549, +0.0595] | disconfirmed |
| S5 | 3 | -0.0314 | [-0.0343, -0.0285] | supported |
| S5 | 5 | -0.0549 | [-0.0590, -0.0508] | supported |
| S5 | 9 | -0.0850 | [-0.0893, -0.0808] | supported |
| S5 | 15 | -0.1112 | [-0.1152, -0.1071] | supported |
| S5 | 31 | -0.1242 | [-0.1280, -0.1204] | supported |
| S6 | 3 | +0.0066 | [+0.0043, +0.0089] | disconfirmed |
| S6 | 5 | +0.0209 | [+0.0183, +0.0235] | disconfirmed |
| S6 | 9 | +0.0475 | [+0.0446, +0.0505] | disconfirmed |
| S6 | 15 | +0.0709 | [+0.0679, +0.0738] | disconfirmed |
| S6 | 31 | +0.1047 | [+0.1021, +0.1073] | disconfirmed |

All 240 primary-family cells, the 45 P3 comparisons, the 120 descriptive CW cells and the secondary metrics are in `results/EXP-002/analysis/analysis.md` and `results/EXP-002/report.md`.

## S3. EXP-003: matched cells with sign disagreement

Table S3. The 16 of 48 matched cells where the exact sign of `Delta_MV` differs between models. Source: `results/EXP-003/analysis/analysis.json` (`disagreeing_cells`, `negative_cells`) and the generated table in `results/EXP-003/report.md`.

| p | r | n | Negative models (exact `Delta_MV`) | Positive models |
|---|---|---|---|---|
| 0.55 | 0.2 | 9 | Bahadur -0.02314 | common-shock, mixture, Beta |
| 0.55 | 0.2 | 15 | mixture -0.01461 | common-shock, Beta (Bahadur excluded) |
| 0.55 | 0.4 | 3 | Bahadur -0.00495, mixture -0.00495 | common-shock, Beta |
| 0.55 | 0.4 | 5 | Bahadur -0.03038, mixture -0.01568 | common-shock, Beta |
| 0.55 | 0.4 | 9 | mixture -0.03258 | common-shock, Beta (Bahadur excluded) |
| 0.55 | 0.4 | 15 | mixture -0.04417 | common-shock, Beta (Bahadur excluded) |
| 0.6 | 0.2 | 9 | Bahadur -0.03378 | common-shock, mixture, Beta |
| 0.6 | 0.2 | 15 | mixture -0.01579 | common-shock, Beta (Bahadur excluded) |
| 0.6 | 0.4 | 3 | Bahadur -0.00960, mixture -0.00960 | common-shock, Beta |
| 0.6 | 0.4 | 5 | Bahadur -0.05568, mixture -0.02803 | common-shock, Beta |
| 0.6 | 0.4 | 9 | mixture -0.05667 | common-shock, Beta (Bahadur excluded) |
| 0.6 | 0.4 | 15 | mixture -0.07927 | common-shock, Beta (Bahadur excluded) |
| 0.7 | 0.4 | 3 | Bahadur -0.01680, mixture -0.01680 | common-shock, Beta |
| 0.7 | 0.4 | 5 | Bahadur -0.07476, mixture -0.03242 | common-shock, Beta |
| 0.7 | 0.4 | 9 | mixture -0.05591 | common-shock, Beta (Bahadur excluded) |
| 0.7 | 0.4 | 15 | mixture -0.08109 | common-shock, Beta (Bahadur excluded) |

## S4. Exploratory analyses (M4, after all verdicts; EXPLORATORY)

These analyses change no verdict. Full tables: `results/exploratory/m4-analytic/summary.md` (J-0015, closed forms only, `scripts/m4_exploratory_analytic.py`) and `results/exploratory/m4-cw-delta/summary.md` (J-0016, 10 exploratory seeds of 2000 items, entropy 0, configs `configs/exploratory/m4_cw_delta_*.json`, `scripts/m4_cw_delta_summary.py`).

Table S4a. Exact `Delta_MV = A_MV(n) - mu` for selected EXP-002 scenarios (source: `results/exploratory/m4-analytic/summary.md`, X1).

| Scenario | lambda | n = 3 | n = 31 | n = 101 | n = 301 | limit |
|---|---|---|---|---|---|---|
| S4 | 0 | +0.00960 | -0.05618 | -0.05999 | -0.06000 | -0.06000 |
| S4 | 0.25 | +0.00810 | -0.01444 | -0.02315 | -0.03690 | -0.06000 |
| S5 | 0 | +0.06225 | +0.19973 | +0.18124 | +0.15817 | +0.15000 |
| S5 | 0.25 | +0.05252 | +0.13517 | +0.16293 | +0.19370 | +0.24000 |
| S6 | 0 | -0.01275 | -0.12881 | -0.14951 | -0.15000 | -0.15000 |
| S6 | 0.25 | -0.01076 | -0.05215 | -0.04510 | -0.03311 | +0.02500 |
| S1 | 0.25 | +0.04050 | +0.10900 | +0.06249 | +0.01635 | +0.00000 |

Table S4b. Exact `Delta_MV = A_MV(n) - p` beyond the EXP-003 grid, `p = 0.55` (source: same file, X2).

| Model | r | n = 31 | n = 301 | n = 1001 | limit |
|---|---|---|---|---|---|
| mixture | 0.05 | +0.05682 | -0.04181 | -0.04998 | -0.05000 |
| Beta | 0.05 | +0.08861 | +0.11751 | +0.12075 | +0.12220 |
| mixture | 0.4 | -0.04968 | -0.05000 | -0.05000 | -0.05000 |
| Beta | 0.4 | +0.01276 | +0.01362 | +0.01369 | +0.01372 |

Table S4c. CW and MV against SINGLE at `lambda = 0`, `B = 31`, by confidence informativeness `delta` (confirmatory value 1); 10 exploratory seeds (source: `results/exploratory/m4-cw-delta/summary.md`).

| delta | S4 CW [t95] | S6 CW [t95] | S4 MV | S6 MV |
|---|---|---|---|---|
| 0 | -0.0529 [-0.0591, -0.0467] | -0.1197 [-0.1252, -0.1143] | -0.0573 | -0.1304 |
| 0.25 | -0.0273 [-0.0322, -0.0223] | -0.0543 [-0.0599, -0.0488] | -0.0573 | -0.1304 |
| 0.5 | +0.0312 [+0.0257, +0.0366] | +0.0554 [+0.0482, +0.0626] | -0.0573 | -0.1304 |
| 1 | +0.2090 [+0.2000, +0.2179] | +0.2661 [+0.2576, +0.2747] | -0.0573 | -0.1304 |

MV does not depend on `delta`, so its column repeats. The exploratory seeds differ from the confirmatory ones, so the `delta = 1` row approximates but does not reproduce EXP-002 (S6 CW +0.2628 there).

## S5. Deviations, owner decisions and exploratory exposure

| Item | Date | What | Effect on results |
|---|---|---|---|
| Amendments 1 to 6 (owner) | 2026-11-24 | 30 seeds; DELIB dropped; EXP-004 optional; Bahadur exclusions reported; commands updated and shared seeds (D-008); pre-freeze exploratory S1/S4 values disclosed | Applied before the freeze; part of the frozen design |
| A-3 not adopted | 2026-11-24 | Confidence model kept as drafted | CW is descriptive; limitation |
| D-011 (session, before any confirmatory output) | 2026-11-25 | Operational readings of the frozen rules: Holm p below 0.05; unadjusted t95 for P1 to P3; consecutive `lambda` steps for P3; exact signs for EXP-003 including the beta-binomial closed form for the Beta model (the EXP-003 protocol text expected Monte Carlo for that model); `tie_coin` as the tie-factor reference in EXP-004 | Interpretations stated in each report; no data seen when fixed |
| D-012 | 2026-11-25 | EXP-004 `results.json` and `metrics.csv` (22 MB folder) git-ignored, regenerable; other outputs committed | None on values; SHA-256 manifest committed |
| D-013 (owner) | 2026-11-25 | Missing reports written from committed results only, by the coordinator | No number changed |
| M4 correction (D-014) | 2026-11-25 | EXP-002 report and CLM-002 said 24 MV and 8 SEQ rejected cells; the committed analysis gives 20 and 12 | Text corrected; no verdict changed |
| M4 exploratory checks (D-014) | 2026-11-25 | J-0015 closed forms, J-0016 CW `delta` sweep with exploratory seeds | Exploratory; no verdict changed |
| Deviations from the frozen protocols | | None | |

**Exploratory exposure before the freeze.** The smoke run (`results/exploratory/smoke/`, 2 seeds of 200 items) and the seed-spread probe (`results/exploratory/probe-seed-spread/`, 10 seeds of 2000 items) produced values of the primary contrast for S1 and S4 at `lambda` in {0, 0.5}, with exploratory seed entropy 0. They were used only to set the seed count. An engine-validation probe (`results/exploratory/probe-engine-validation/`) and a timing-only EXP-003 draft run (J-0007, outcomes not inspected or committed) were also made. The M3 smoke run (`results/exploratory/m3-smoke/`) and metric check (32 of 32) preceded the confirmatory runs. No confirmatory run failed, so no failed run is missing from this account.

## S6. Reports and records

- Experiment reports: [`EXP-001`](../experiments/EXP-001/report.md), [`EXP-002`](../experiments/EXP-002/report.md), [`EXP-003`](../experiments/EXP-003/report.md), [`EXP-004`](../experiments/EXP-004/report.md), each with `reproduction.md`.
- Figures: FIG-001-1 `../experiments/EXP-001/figures/z_histogram.png`; FIG-002-1 `../experiments/EXP-002/figures/FIG-002-1_delta_vs_budget.png`; FIG-003-1 `../experiments/EXP-003/figures/FIG-003-1_delta_by_model.png`; FIG-004-1 to FIG-004-3 in `../experiments/EXP-004/figures/`. Each is byte-identical to the file generated in `results/EXP-00N/`.
- Records: `research/claims_register.csv`, `research/decision_log.md`, `research/experiment_journal.jsonl`, `research/limitations.md`, `research/publication/evidence_audit.md`, `research/publication/review_pass_2.md`.
