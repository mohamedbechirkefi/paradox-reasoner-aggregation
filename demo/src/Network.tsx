// SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
// Reasoning network for one sandbox item: the shared (common-shock) answer in
// the centre, the B reasoners on a ring. A line from the centre marks a
// reasoner that adopted the shared answer, so a wrong shared answer visibly
// propagates to every adopter. In SEQ mode the numbers give the speaking order
// and a double ring marks a reasoner that followed the leader of the earlier
// public tally. Drawn from sandbox output only.
import { MAX_REASONERS, seqItem, type Draws } from "./engine";
import type { ItemDetail } from "./sandboxTypes";

function asDraws(it: ItemDetail): Draws {
  const J = MAX_REASONERS;
  return {
    nItems: 1,
    y: Uint8Array.of(it.y),
    hard: Uint8Array.of(it.hard),
    pItem: Float64Array.of(it.pItem),
    leaderCorrect: Uint8Array.of(it.leaderCorrect),
    adopt: Uint8Array.from(it.adopt.slice(0, J)),
    correct: Uint8Array.from(it.correct.slice(0, J)),
    seqKey: Float64Array.from(it.seqKey.slice(0, J)),
    herdU: Float64Array.from(it.herdU.slice(0, J)),
    tieCoin: Uint8Array.of(it.tieCoin),
  };
}

export interface NetworkSummary {
  text: string;
  mvCorrect: boolean;
  seqCorrect: boolean;
}

function decide(k: number, n: number, coin: number): boolean {
  return 2 * k === n ? coin === 1 : 2 * k > n;
}

export function summarizeItem(it: ItemDetail, n: number, w: number, index: number): NetworkSummary {
  const s = seqItem(asDraws(it), 0, n, w);
  const adopters = it.adopt.slice(0, n).reduce((a, b) => a + b, 0);
  const kMv = it.correct.slice(0, n).reduce((a, b) => a + b, 0);
  const kSeq = s.votes.reduce((a, b) => a + b, 0);
  const herded = s.herded.filter(Boolean).length;
  const mvCorrect = decide(kMv, n, it.tieCoin);
  const seqCorrect = decide(kSeq, n, it.tieCoin);
  const text =
    `Item ${index + 1}: ${it.hard ? "hard" : "easy"} item, each reasoner correct with probability ${it.pItem}. ` +
    `The shared answer is ${it.leaderCorrect ? "correct" : "wrong"} and ${adopters} of ${n} reasoners adopted it. ` +
    `Answers: ${kMv} of ${n} correct, so the majority vote is ${mvCorrect ? "correct" : "wrong"}. ` +
    `In sequential voting ${herded} reasoners followed the leader and ${kSeq} of ${n} public votes are correct, so SEQ is ${seqCorrect ? "correct" : "wrong"}. ` +
    `SINGLE (reasoner 1) is ${it.correct[0] ? "correct" : "wrong"}.`;
  return { text, mvCorrect, seqCorrect };
}

export function Network({ item, n, w, mode, index }: { item: ItemDetail; n: number; w: number; mode: "MV" | "SEQ"; index: number }) {
  const s = seqItem(asDraws(item), 0, n, w);
  const sum = summarizeItem(item, n, w, index);
  const size = 440;
  const c = size / 2;
  const R = n > 15 ? 168 : 150;
  const rNode = n > 15 ? 11 : 15;
  const rank = new Map(s.order.map((j, t) => [j, t]));
  const pos = (j: number) => {
    const t = mode === "SEQ" ? rank.get(j)! : j;
    const a = -Math.PI / 2 + (2 * Math.PI * t) / n;
    return { x: c + R * Math.cos(a), y: c + R * Math.sin(a) };
  };
  const shown = (j: number) => (mode === "SEQ" ? s.votes[j] : item.correct[j]);

  return (
    <figure className="network">
      <svg viewBox={`0 0 ${size} ${size}`} role="img" aria-labelledby="net-title net-desc">
        <title id="net-title">Reasoning network for sandbox item {index + 1}, {mode === "SEQ" ? "sequential public votes" : "answers"}</title>
        <desc id="net-desc">{sum.text}</desc>
        {Array.from({ length: n }, (_, j) =>
          item.adopt[j] ? (
            <line key={`e${j}`} className={`edge ${item.leaderCorrect ? "ok" : "bad"}`} x1={c} y1={c} x2={pos(j).x} y2={pos(j).y} />
          ) : null,
        )}
        {mode === "SEQ" &&
          s.order.slice(1).map((j, t) => {
            const a = pos(s.order[t]);
            const b = pos(j);
            return <line key={`o${j}`} className="order" x1={a.x} y1={a.y} x2={b.x} y2={b.y} />;
          })}
        <circle className={`hub ${item.leaderCorrect ? "ok" : "bad"}`} cx={c} cy={c} r={34} />
        <text className="hub-label" x={c} y={c - 4} textAnchor="middle">shared</text>
        <text className="hub-label" x={c} y={c + 14} textAnchor="middle">{item.leaderCorrect ? "correct" : "wrong"}</text>
        {Array.from({ length: n }, (_, j) => {
          const p = pos(j);
          const ok = shown(j) === 1;
          return (
            <g key={`n${j}`}>
              {mode === "SEQ" && s.herded[j] && <circle className="herd" cx={p.x} cy={p.y} r={rNode + 4} />}
              <circle className={`node ${ok ? "ok" : "bad"}`} cx={p.x} cy={p.y} r={rNode} />
              {!ok && (
                <path className="cross" d={`M${p.x - rNode * 0.45},${p.y - rNode * 0.45} L${p.x + rNode * 0.45},${p.y + rNode * 0.45} M${p.x + rNode * 0.45},${p.y - rNode * 0.45} L${p.x - rNode * 0.45},${p.y + rNode * 0.45}`} />
              )}
              {mode === "SEQ" && (
                <text className="node-label" x={c + (p.x - c) * ((R + rNode + 12) / R)} y={c + (p.y - c) * ((R + rNode + 12) / R) + 4} textAnchor="middle">
                  {rank.get(j)! + 1}
                </text>
              )}
            </g>
          );
        })}
      </svg>
      <figcaption>
        <p className="chart-desc">{sum.text}</p>
        <ul className="legend">
          <li><svg width="18" height="18" aria-hidden="true"><circle className="node ok" cx={9} cy={9} r={7} /></svg> correct answer</li>
          <li>
            <svg width="18" height="18" aria-hidden="true"><circle className="node bad" cx={9} cy={9} r={7} /><path className="cross" d="M6,6 L12,12 M12,6 L6,12" /></svg> wrong
            answer
          </li>
          <li><svg width="26" height="10" aria-hidden="true"><line className="edge bad" x1={1} x2={25} y1={5} y2={5} /></svg> adopted the shared answer (common shock)</li>
          {mode === "SEQ" && (
            <li><svg width="22" height="22" aria-hidden="true"><circle className="herd" cx={11} cy={11} r={9} /></svg> followed the leader of the earlier votes; numbers give the speaking order</li>
          )}
        </ul>
      </figcaption>
    </figure>
  );
}
