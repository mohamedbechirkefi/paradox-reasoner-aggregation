// SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
// Bounded sandbox computation in a Web Worker. It runs the browser port of the
// engine (engine.ts) for at most MAX_ITEMS items and 31 reasoners. Cancellation
// terminates the worker from the page, so no partial result is ever shown.
import { generateDraws, MAX_REASONERS, summarize } from "./engine";
import { DETAIL_ITEMS, SANDBOX_BUDGETS, type ItemDetail, type WorkerReply, type WorkerRequest } from "./sandboxTypes";

onmessage = (ev: MessageEvent<WorkerRequest>) => {
  const m = ev.data;
  if (m.type !== "run") return;
  try {
    const t0 = performance.now();
    const p = m.params;
    postMessage({ type: "progress", stage: "drawing" } satisfies WorkerReply);
    const d = generateDraws(p.scenario, p.lam, p.nItems, p.seed);
    postMessage({ type: "progress", stage: "aggregating" } satisfies WorkerReply);
    const rows = SANDBOX_BUDGETS.map((b) => ({ budget: b, ...summarize(d, b, p.w) }));
    const J = MAX_REASONERS;
    const items: ItemDetail[] = [];
    for (let i = 0; i < Math.min(DETAIL_ITEMS, d.nItems); i++) {
      const sl = <T extends Uint8Array | Float64Array>(a: T) => Array.from(a.slice(i * J, (i + 1) * J));
      items.push({
        y: d.y[i], hard: d.hard[i], pItem: d.pItem[i], leaderCorrect: d.leaderCorrect[i],
        adopt: sl(d.adopt), correct: sl(d.correct), seqKey: sl(d.seqKey), herdU: sl(d.herdU), tieCoin: d.tieCoin[i],
      });
    }
    postMessage({ type: "done", result: { params: p, rows, items, ms: performance.now() - t0 } } satisfies WorkerReply);
  } catch (e) {
    postMessage({ type: "error", message: e instanceof Error ? e.message : String(e) } satisfies WorkerReply);
  }
};
