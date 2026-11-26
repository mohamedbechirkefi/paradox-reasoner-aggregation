<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# PARADOX demo: design plan (owner request 2026-11-26)

## Subject, audience, job

- **Subject.** Twelve-person juries, ballots and tallies: the Condorcet jury theorem and how it fails. More votes amplify whatever the typical reasoner does, so a majority of competent reasoners gets better with size and a majority on items most reasoners get wrong locks in the wrong answer. Correlated errors and herding (sequential public votes) change how strongly.
- **Audience.** A curious technical reader first, then an admissions committee reading quickly, then a researcher who wants the intervals, the Holm-rejected cells and the hashes.
- **Primary job.** State the question and the answer in one sentence, then show the answer as the study's own kind of picture: accuracy against budget, with the zero line as "one reasoner, one call". Everything else (verdicts, tables, sandbox, limitations, reproduction) is evidence underneath.

## Colour (light only)

| Name | Hex | Role |
| --- | --- | --- |
| Slate board | `#25352F` | the hero deliberation board and the footer; green-grey slate, not black |
| Chalk | `#ECEFE6` | text and tally marks on the slate |
| Tally yellow | `#E2C04A` | chalk tally marks and the hero stamp outline, only on slate |
| Ballot paper | `#F0F2EC` | page field: a cool, slightly green official-form paper, never cream |
| Jury ink | `#1E2B3C` | body text, MV series, "correct" in figures |
| Seal red | `#A3262C` | wrong answers, Holm-rejected (degradation) cells, the X in the wordmark |

Derived for data only: SEQ series in a darkened tally ochre `#7F6210`, CW series in a slate green `#3F6A5A`, both checked for 4.5:1 on ballot paper. One colour means one thing: red is always "wrong" or "degradation detected".

The brand is light only. A dark slate field already carries the hero; a full dark theme would turn the ballot paper into the near-black-plus-accent default. `color-scheme: light` is declared.

## Type

- **Zilla Slab** (Mozilla, SIL OFL 1.1), 600 and 700: display and headings, experiment ids, the wordmark. A slab reads as printed forms, docket headers and ballot papers rather than as a magazine.
- **Public Sans** (USWDS, SIL OFL 1.1), 400 and 600: body, controls, tables. A civic typeface made for official forms; tabular figures for every number.
- Scale (1.25 ratio): 14, 16, 18, 22.5, 28, 35, 44, 55 px. Body 17 px, line-height 1.6, measure at most 68 characters. Headings sentence case, no tracked capitals.

## Layout

Left-aligned throughout; the measure is held to about 68 characters and figures run wider than text.

```
+--------------------------------------------------------------+
| [mark] Paradox        Curves  Verdicts  Sandbox  Method  ... |  sticky ballot-paper bar
+==============================================================+
| SLATE BOARD                                                  |
|  When more reasoners          |  Illustration, not study data|
|  make worse decisions         |  [ballot][ballot] ... x12    |
|                               |  Right  |||| ||              |
|  Question. Answer sentence    |  Wrong  |||| |||            |
|  with the S6 estimate.        |  (Easy item | Hard item)     |
|  author line                  |  stamp: Majority wrong       |
+==============================================================+
| Accuracy and cost curves (the key result)                    |
|  [scenario v] [lambda v]  (Calls | Calls plus messages)      |
|  +--------------------------------------------------------+  |
|  |  chart, zero line = SINGLE, red rings = Holm-rejected  |  |
|  +--------------------------------------------------------+  |
| Verdicts: docket of EXP-001..004 and exploratory checks      |
| Published results: one ballot-form panel per experiment      |
| Sandbox (dashed ballot-box border) + reasoning network       |
| Assumptions | Method and limitations | Reproduce             |
+--------------------------------------------------------------+
| SLATE footer: links, licence, AI-use, fonts                  |
+--------------------------------------------------------------+
```

Panels are not identical cards: experiment panels are ballot forms (a heavy ink top rule with the id set in slab, a perforated left edge), the sandbox is a dashed "ballot box", assumptions a two-column register. Radii are small (2 to 4 px) and vary with role.

## Motion

- **The orchestrated hero moment.** Twelve ballot slips drop onto the board in turn (60 ms stagger, translate and small rotation, opacity), each is marked with a tick or a cross, and one chalk stroke per slip is drawn into the "Right" or "Wrong" tally (scaleY from the top, the fifth stroke strikes the gate). Finally a stamp lands: "Majority: wrong" on the hard item. It plays once on load; a segmented control (Easy item, Hard item) replays it for the other item. Labelled "Illustration, not study data" and showing no numerals at all, only tally marks and words.
- **Motion that answers actions.** Chart series reveal once when the chart scrolls into view (clip-path wipe along the budget axis, 600 ms strong ease-out); segmented-control indicators slide (transform, 220 ms); the sandbox Run button shows a counting state and the new output line settles in (opacity and 6 px translate, 240 ms) when a run returns.
- Curves: `cubic-bezier(0.23, 1, 0.32, 1)` for entrances, `cubic-bezier(0.77, 0, 0.175, 1)` for on-screen movement. No `transition: all`. Hover motion only inside `(hover: hover) and (pointer: fine)`. Under reduced motion every animation is replaced by its final state or an opacity change.
- No motion on select changes, table toggles or anything a visitor repeats tens of times.

## The one memorable thing

The chalk tally board: twelve ballots counted into tally gates, with the majority stamp flipping from right to wrong when the item gets hard. The wordmark echoes it: the X of "Paradox" is a seal-red ballot cross.

## Review against the generated-page tells, and what changed

- First draft used a full chalkboard dark theme with chalk-white text and one yellow accent. That is the near-black-plus-one-accent default in green clothing. Changed: slate is limited to the hero and footer; the reading surface is ballot paper with ink.
- First draft paper was a warm off-white. Too close to the cream tell. Changed to a cool green-grey ballot paper `#F0F2EC`, and the accent is a seal red, not terracotta.
- First draft put a tracked all-caps "PRELIMINARY VERDICT" eyebrow over each section. Removed; headings stand alone, and labels say what the evidence is in sentence case.
- First draft numbered the sections 01 to 06. The sections are not a sequence; removed. The tally gates are the only counting device, and they count ballots.
- First draft used a monospace face for ids and hashes. Ids are set in the slab; hashes keep the system monospace only inside `code`, where they are code.
- Compared with the other studies' directions: HERD shows a chain of decisions left to right; PARADOX stays in the jury room (simultaneous ballots, tally, stamp). TRUST is a white test-lab report; MEMORY uses index cards and pencil; PARADOX uses slate, chalk and printed ballot forms.
