<!-- SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0 -->
# Claims audit (checklist; not started)

Status at M0: no claims exist (`research/claims_register.csv` has a header row only).

For every row of the claims register, before release:

- [ ] Claim text matches the manuscript, reports, README, demo and articles word for word in scope.
- [ ] Type is correct (observed, inferred, simulated, external).
- [ ] Evidence path exists and resolves to a result file, run id and figure or table id.
- [ ] Number recomputed from raw output; denominator, unit, precision, interval and sample count checked.
- [ ] External claims map to a source listed as verified in `literature_review.md`.
- [ ] Limitations column filled; synthetic scope stated.
- [ ] Second-pass review challenged the preferred hypothesis (record reviewer and date).
