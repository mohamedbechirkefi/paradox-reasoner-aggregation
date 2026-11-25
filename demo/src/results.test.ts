// SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { ResultsError, validateResults } from "./results";

const good = () => JSON.parse(readFileSync("public/data/results.json", "utf8"));

describe("validateResults", () => {
  it("accepts the exported results file", () => {
    expect(validateResults(good()).experiments.length).toBeGreaterThan(0);
  });
  it("rejects a wrong schema name", () => {
    expect(() => validateResults({ ...good(), schema: "other" })).toThrow(ResultsError);
  });
  it("rejects an unsupported major version", () => {
    expect(() => validateResults({ ...good(), schema_version: "2.0.0" })).toThrow(ResultsError);
  });
  it("rejects a missing estimate", () => {
    const r = good();
    delete r.experiments[0].estimates?.[0]?.estimate;
    if (r.experiments[0].estimates.length === 0) r.experiments[0].title = 7;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a non-finite number", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: "NaN", ci_low: null, ci_high: null, ci_level: null, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a half-open interval", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: 1, ci_low: 0, ci_high: null, ci_level: 0.95, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a malformed source hash", () => {
    expect(() => validateResults({ ...good(), sources: [{ path: "a", sha256: "zz" }] })).toThrow(ResultsError);
  });
  it("rejects missing curves", () => {
    const r = good();
    delete r.curves;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a curve point outside its interval", () => {
    const r = good();
    const p = r.curves.points.find((x: { budget: number }) => x.budget === 31);
    p.delta = p.ci_high + 0.1;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a curve display string that differs from its value", () => {
    const r = good();
    r.curves.points[5].delta_display = "0.9999";
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an unknown rule or scenario in the curves", () => {
    const r = good();
    r.curves.points[0].rule = "DELIB";
    expect(() => validateResults(r)).toThrow(ResultsError);
    const q = good();
    q.curves.points[0].scenario = "S9";
    expect(() => validateResults(q)).toThrow(ResultsError);
  });
  it("rejects a malformed scenario, rejected cell, exception or sandbox block", () => {
    const a = good(); a.scenarios[0].h = 2;
    expect(() => validateResults(a)).toThrow(ResultsError);
    const b = good(); b.holm_rejected[0].budget = 40;
    expect(() => validateResults(b)).toThrow(ResultsError);
    const c = good(); c.display_exceptions[0].source = "";
    expect(() => validateResults(c)).toThrow(ResultsError);
    const d = good(); d.sandbox.confirmatory_seeds_first = [];
    expect(() => validateResults(d)).toThrow(ResultsError);
  });
  it("keeps every experiment, including null, disconfirmed and exploratory ones", () => {
    const ids = validateResults(good()).experiments.map((e) => e.id);
    expect(ids).toEqual(["EXP-001", "EXP-002", "EXP-003", "EXP-004", "J-0015", "J-0016"]);
  });
});
