<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# EXP-004 protocol: robustness to secondary design choices (optional)

**Status: FROZEN v1.0 (owner-approved 2026-11-24). Drafted as v0.1 on 2026-11-24. The SHA-256 of this file and of `config.json` is recorded in `research/freeze.json` and in the registry. Optional (confirmed by the owner): first item cut if the five-day target is threatened; a cut is reported. Depends on EXP-002.**

## 1. Question

Are the EXP-002 conclusions robust to the tie rule at even budgets, to counting messages read as cost, to confidence miscalibration and to herding strength?

## 2. Factors (one at a time, around the EXP-002 primary setting)

| Factor | Levels | Rules affected |
|---|---|---|
| Tie rule at even `B` in {2, 4, 8, 16, 30} | seeded coin flip (primary); abstain counted as wrong | MV, SEQ |
| Cost accounting | calls (primary); calls plus messages read | SEQ |
| Confidence scale `tau` | 0.5, 1 (primary), 2, 4 | CW, calibration metrics |
| Herding `w` | 0.25, 0.5 (primary), 0.9 | SEQ |

Scenarios S1, S4, S5; `lambda` in {0, 0.5}; 30 seeds (amendment 1; was 10), the same list in every cell (D-008); 2000 items. DELIB is dropped (amendment 2), so the cost and herding factors apply to SEQ only.

Implementation (`config.json`): one config with eight variants that each override one factor of the primary setting: `primary` (EXP-002 setting; also the reference for the cost factor, which is computed from `messages_per_item` of SEQ and needs no separate run), `tie_coin` and `tie_abstain_wrong` (even budgets {2, 4, 8, 16, 30} plus the SINGLE baseline; MV and SEQ), `tau_0p5`, `tau_2`, `tau_4`, `w_0p25`, `w_0p9`. With the shared seeds, the `primary` variant reproduces the corresponding EXP-002 cells exactly, which serves as a consistency check.

## 3. Hypotheses

- **H0:** for every factor level, the sign of `Delta_r` in each EXP-002 cell that was significant (Holm) is unchanged.
- **H1:** at least one factor level reverses a sign.
- This is a robustness check; a reversal is reported as a limitation of the EXP-002 conclusion, not as a new finding.

## 4. Uncertainty, exclusion, stopping

As EXP-002. With calls plus messages, budget equality is broken; comparisons are then reported as accuracy against cost curves, not as matched-budget contrasts.

## 5. Reproduction

```
uv run paradox run --config research/experiments/EXP-004/config.json --out results/EXP-004/ --pdf
uv run paradox report results/EXP-004/ --pdf
```

`paradox run` refuses the config unless its hash and this protocol's hash match `research/freeze.json`.

## Amendments before freeze (owner-approved 2026-11-24)

Approved by the owner on 2026-11-24 and applied before the freeze and before any confirmatory run (full list: `research/protocol.md` section 10; approval quoted in `research/freeze.json`).

- **Optional status kept** (header). Decision O-5.
- **Seeds:** 30 (was 10) (section 2).
- **DELIB dropped:** the cost and herding factors now apply to SEQ only (section 2).
- **Shared seeds** across cells confirmed (section 2).
- **Commands:** `paradox report EXP-004` replaced by `paradox report <results folder>` (section 5).
- **Implementation note (not an amendment):** the tie level "abstain counted as wrong", drafted in v0.1, was implemented at the freeze (`tie_rule = abstain_wrong`, tested in `tests/test_rules.py` and `tests/test_pipeline.py`), together with the variant mechanism described in section 2.
