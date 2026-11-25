// SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
// The browser port must reproduce the Python engine. Fixture written by
// scripts/export_sandbox_fixture.py from src/paradox and from the committed
// results/EXP-002/metrics.csv. Tolerance: exact. Draws are compared with ===;
// correct-decision counts are equal; committed accuracies (count / 2000) agree
// to 1e-12, which at 2000 items means the same integer count.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { generateDraws, MAX_REASONERS, seqItem, streamRng, summarize } from "./engine";

const fx = JSON.parse(readFileSync("src/fixtures/engine_fixture.json", "utf8"));

describe("engine port against the Python engine", () => {
  for (const c of fx.cases) {
    it(`stream draws are identical (${c.name})`, () => {
      for (const [name, heads] of Object.entries(c.stream_heads as Record<string, number[]>)) {
        const g = streamRng(c.seed, name as Parameters<typeof streamRng>[1]);
        for (const x of heads) expect(g.random()).toBe(x);
      }
    });
    it(`SINGLE, MV and SEQ counts are identical at every budget (${c.name})`, () => {
      const d = generateDraws(c.scenario, c.lam, c.n_items, c.seed);
      for (const [b, want] of Object.entries(c.counts)) {
        expect(summarize(d, Number(b), c.w)).toEqual(want);
      }
      expect(Array.from(d.correct.slice(0, MAX_REASONERS))).toEqual(c.item0_correct);
      expect(seqItem(d, 0, 9, c.w).votes).toEqual(c.item0_seq_votes_b9);
    });
  }

  it("reproduces a committed confirmatory EXP-002 seed-run", () => {
    const r = fx.committed_seed_run;
    const d = generateDraws(r.scenario, r.lam, r.n_items, r.seed);
    expect(r.rows.length).toBeGreaterThan(0);
    for (const row of r.rows) {
      const s = summarize(d, row.budget, r.w);
      const k = row.rule === "SINGLE" ? s.single : row.rule === "MV" ? s.mv : s.seq;
      expect(Math.abs(k / r.n_items - row.accuracy)).toBeLessThan(1e-12);
    }
  });

  it("rejects out-of-range inputs", () => {
    const sc = { p_easy: 0.6, h: 0, p_hard: 0.6 };
    expect(() => generateDraws(sc, 1.5, 10, 1)).toThrow();
    expect(() => generateDraws(sc, 0, 0, 1)).toThrow();
    expect(() => generateDraws(sc, 0, 10, -1)).toThrow();
    expect(() => generateDraws(sc, 0, 10, 2 ** 32)).toThrow();
    const d = generateDraws(sc, 0, 10, 1);
    expect(() => summarize(d, 32, 0.5)).toThrow();
    expect(() => summarize(d, 3, 2)).toThrow();
  });
});
