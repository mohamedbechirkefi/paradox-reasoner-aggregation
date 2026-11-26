<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
<!-- Draft for Medium (master prompt section 8). Not published; publication is the owner's decision. Every number is printed in research/paper/manuscript.md. -->

# When more reasoners make worse decisions: a preregistered simulation of voting at equal compute

*Draft. Independent research, not peer-reviewed. Synthetic reasoners, not language models or people.*

Ask one fallible reasoner a yes-or-no question and it is right some of the time. Ask 31 of them and take the majority, and you might expect to be right far more often. That is the promise of the Condorcet jury theorem, and it is the intuition behind many systems that sample several answers and vote. The theorem has conditions, though: each voter must be better than a coin flip, and their errors must be independent. This project asked what happens, at a fixed budget of calls, when those conditions fail.

## The question

Under an equal compute budget, when does aggregation of fallible reasoners improve or degrade accuracy?

Each item is a binary decision. A budget of `B` calls buys `B` votes. Three rules spend it: majority vote (MV), confidence-weighted vote (CW) and sequential public voting, where each reasoner sees the earlier votes and may follow the leader (SEQ). Each is compared with one reasoner making one call.

## How the simulation works

The reasoners are deliberately simple: each answers correctly with a set probability. Two features make them interesting. First, items differ in difficulty: in some scenarios a large share of items is "hard", and on those a reasoner is right less than half the time. Second, errors can be correlated: with probability `lambda` a reasoner adopts a shared answer for the item instead of answering on its own, so one wrong shared answer spreads to everyone who adopted it.

Four experiments were written down, with their decision rules, and frozen by the owner before any confirmatory run. The primary experiment used six scenarios, four correlation levels and 30 seeds of 2000 items per cell, with paired comparisons and intervals at the level of the seed-run.

*Figure suggestion: the demo's accuracy and cost curves for scenario S6 at `lambda = 0` (alt text: majority voting falls further below a single call as the budget grows to 31 calls; sequential voting falls less; vertical bars are 95% intervals).*

## What was found

**The engine is validated.** Simulated majority accuracy matched exact formulas in all 292 admissible validation cells, within 4 Monte Carlo standard errors (largest deviation 3.116).

**More votes can make things worse.** In 32 of 240 majority and sequential cells, accuracy was detectably below one call after correcting for multiple comparisons, all in the two scenarios where many items are below chance. The largest loss: majority voting in scenario S6 with independent errors and 31 calls, -0.1313 accuracy (95% interval -0.1350 to -0.1276). In S6, half the items are hard; a single call is right on them 35% of the time, and a majority of 31 almost never is, while the easy items were already nearly always right. This is what the exact formulas predict, and the experiment confirms it rather than discovering it.

**A prediction failed.** The preregistered prediction was that sequential voting, where reasoners can follow the crowd, would do worse than majority voting. Where aggregation helps, it did. Where majority voting degrades, sequential voting lost less (up to +0.1047 [+0.1021, +0.1073] better than majority voting in S6), though it still lost accuracy there (-0.0266 at 31 calls). The prediction is reported as disconfirmed. It concerns one sequential rule only.

**The answer depends on the model of dependence.** At matched individual accuracy and matched pairwise correlation, four different models of dependence disagreed on whether majority voting helps or hurts in 16 of 48 cells. Pairwise correlation is not enough to know the sign, and the degradation result holds only within the two model families studied.

**A robustness check found nothing, but checked little.** Changing the tie rule, the confidence scale, the herding strength or the cost accounting reversed no significant result (0 of 18 checks), but only 3 of the 32 significant cells were in its scope.

**Confidence weighting looked excellent for a boring reason.** CW beat one call everywhere, by up to +0.4478, but an exploratory check showed this comes from the assumed confidence signal. With uninformative confidence, CW degrades like majority voting.

## Limitations

These are synthetic Bernoulli reasoners, not language models, committees or people; nothing here is a benchmark of any real system. Budgets stop at 31 calls, and with correlation the sign at 31 calls can differ from the large-budget limit. Cells share seeds, so counts of significant cells are not counts of independent findings. The literature search was targeted, and most sources were read at abstract level. The analysis and the review of it were made with an AI research assistant; the owner's full-text review of the manuscript is pending.

## Reproduce it

The code, frozen protocols, raw results, reports, manuscript and an offline interactive page are in the repository: https://github.com/mohamedbechirkefi/paradox-reasoner-aggregation. Demo: https://paradox-reasoner-aggregation.kefimohamedbechir.workers.dev.
