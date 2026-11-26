<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
<!-- Draft for LinkedIn (master prompt section 8). Not published; publication is the owner's decision. Every number is printed in research/paper/manuscript.md. -->

More votes are not always better.

I built PARADOX, a small preregistered simulation, with an AI system as a disclosed research and development assistant. It asks: with a fixed budget of calls, when does letting several fallible reasoners vote beat asking one of them once? It has a tested simulation engine validated against exact formulas, four experiments frozen before any confirmatory run, a standalone report for each, a manuscript, and an offline interactive page with a seeded sandbox.

One defensible finding: when half the items are ones a reasoner usually gets wrong, majority voting over 31 independent synthetic reasoners changed accuracy by -0.1313 against a single call (95% interval -0.1350 to -0.1276). This is what the exact formulas predict. Less expected: a preregistered prediction failed, because sequential voting with herding lost less than majority voting in exactly those cases.

Caveat: these are synthetic Bernoulli reasoners, not language models or people, and the degradation result holds only for two of the four dependence models tested. Not peer-reviewed.

Repository: https://github.com/mohamedbechirkefi/paradox-reasoner-aggregation
Demo: https://paradox-reasoner-aggregation.kefimohamedbechir.workers.dev
