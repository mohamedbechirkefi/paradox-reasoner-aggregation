<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# EXP-004 protocol: robustness to secondary design choices (optional)

**Status: DRAFT v0.1, 2026-11-24, awaiting owner freeze (G-FREEZE). Protocol hash: not yet computed. Optional: first item cut if the five-day target is threatened. Depends on EXP-002.**

## 1. Question

Are the EXP-002 conclusions robust to the tie rule at even budgets, to counting messages read as cost, to confidence miscalibration and to herding strength?

## 2. Factors (one at a time, around the EXP-002 primary setting)

| Factor | Levels | Rules affected |
|---|---|---|
| Tie rule at even `B` in {2, 4, 8, 16, 30} | seeded coin flip (primary); abstain counted as wrong | MV, SEQ |
| Cost accounting | calls (primary); calls plus messages read | SEQ, DELIB |
| Confidence scale `tau` | 0.5, 1 (primary), 2, 4 | CW, calibration metrics |
| Herding `w` | 0.25, 0.5 (primary), 0.9 | SEQ, DELIB |

Scenarios S1, S4, S5; `lambda` in {0, 0.5}; 10 seeds; 2000 items.

## 3. Hypotheses

- **H0:** for every factor level, the sign of `Delta_r` in each EXP-002 cell that was significant (Holm) is unchanged.
- **H1:** at least one factor level reverses a sign.
- This is a robustness check; a reversal is reported as a limitation of the EXP-002 conclusion, not as a new finding.

## 4. Uncertainty, exclusion, stopping

As EXP-002. With calls plus messages, budget equality is broken; comparisons are then reported as accuracy against cost curves, not as matched-budget contrasts.

## 5. Reproduction (planned)

```
uv run paradox run --config research/experiments/EXP-004/config.json --out results/EXP-004/
uv run paradox report EXP-004
```
