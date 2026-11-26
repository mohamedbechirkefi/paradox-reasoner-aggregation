// SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
// Hero illustration: twelve ballots for one item are dropped on the table and
// counted into chalk tally gates, then the majority is stamped. It explains the
// mechanism (on an item most jurors get wrong, the majority locks in the wrong
// answer) and is not study data: it prints no numeral and no estimate.
import { useState } from "react";
import { Seg } from "./Seg";

type Kind = "easy" | "hard";

// Fixed ballots (1 = right, 0 = wrong). Easy: most right. Hard: most wrong.
const BALLOTS: Record<Kind, number[]> = {
  easy: [1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1],
  hard: [0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1],
};
const TILT = [-4, 3, -2, 5, -3, 2, 4, -5, 2, -3, 5, -2];

const W = 520;
const H = 336;
const SLIP_W = 58;
const SLIP_H = 70;

function Tick({ x, y }: { x: number; y: number }) {
  return <path className="slip-mark ok" d={`M${x - 11},${y + 1} L${x - 3},${y + 10} L${x + 13},${y - 11}`} />;
}
function Cross({ x, y }: { x: number; y: number }) {
  return <path className="slip-mark bad" d={`M${x - 11},${y - 11} L${x + 11},${y + 11} M${x + 11},${y - 11} L${x - 11},${y + 11}`} />;
}

export function Hero({ children }: { children: React.ReactNode }) {
  const [kind, setKind] = useState<Kind>("hard");
  const ballots = BALLOTS[kind];
  const right = ballots.filter((b) => b === 1).length;
  const majorityRight = 2 * right > ballots.length;

  // Tally geometry: each ballot adds one stroke to its row, in ballot order.
  const rows = { 1: { y: 238, n: 0 }, 0: { y: 298, n: 0 } } as Record<number, { y: number; n: number }>;
  const strokes = ballots.map((b, i) => {
    const row = rows[b];
    const m = row.n++;
    const g = Math.floor(m / 5);
    const k = m % 5;
    const x0 = 132 + g * 84;
    if (k < 4) return { i, kind: "v" as const, x: x0 + k * 15, y: row.y };
    return { i, kind: "d" as const, x: x0 - 8, y: row.y };
  });

  return (
    <header className="hero" id="top">
      <div className="wrap hero-grid">
        <div className="hero-text">{children}</div>
        <figure className="board">
          <p className="illus-label">Illustration, not study data</p>
          <svg
            key={kind}
            className="board-svg"
            viewBox={`0 0 ${W} ${H}`}
            role="img"
            aria-labelledby="board-title"
          >
            <title id="board-title">
              {kind === "hard"
                ? "Illustration: twelve ballots on a hard item. Fewer than half are right, so the majority is wrong."
                : "Illustration: twelve ballots on an easy item. Most are right, so the majority is right."}
            </title>
            {ballots.map((b, i) => {
              const col = i % 6;
              const row = Math.floor(i / 6);
              const x = 26 + col * 80;
              const y = 18 + row * 92;
              return (
                <g key={i} className="slip" style={{ animationDelay: `${180 + i * 70}ms` }}>
                  <g transform={`rotate(${TILT[i]} ${x + SLIP_W / 2} ${y + SLIP_H / 2})`}>
                    <rect className="slip-paper" x={x} y={y} width={SLIP_W} height={SLIP_H} rx={2} />
                    <line className="slip-line" x1={x + 8} x2={x + SLIP_W - 8} y1={y + 12} y2={y + 12} />
                    <rect className="slip-box" x={x + 14} y={y + 24} width={30} height={30} rx={1} />
                    {b ? <Tick x={x + 29} y={y + 39} /> : <Cross x={x + 29} y={y + 39} />}
                  </g>
                </g>
              );
            })}
            <text className="tally-label" x={20} y={246}>Right</text>
            <text className="tally-label" x={20} y={306}>Wrong</text>
            <line className="tally-rule" x1={20} x2={W - 20} y1={266} y2={266} />
            {strokes.map((s) =>
              s.kind === "v" ? (
                <line key={s.i} className="chalk v" x1={s.x} x2={s.x} y1={s.y - 22} y2={s.y + 12} style={{ animationDelay: `${1180 + s.i * 85}ms` }} />
              ) : (
                <line key={s.i} className="chalk d" x1={s.x} x2={s.x + 62} y1={s.y - 14} y2={s.y + 4} style={{ animationDelay: `${1180 + s.i * 85}ms` }} />
              ),
            )}
            <g className={`stamp ${majorityRight ? "is-right" : "is-wrong"}`} style={{ animationDelay: "2380ms" }}>
              <g transform="rotate(-8 420 268)">
                <rect className="stamp-box" x={346} y={244} width={150} height={50} rx={4} />
                <text className="stamp-text" x={421} y={276} textAnchor="middle">
                  {majorityRight ? "Majority right" : "Majority wrong"}
                </text>
              </g>
            </g>
          </svg>
          <figcaption>
            <Seg<Kind>
              title="Item shown"
              ariaLabel="Illustration item"
              tone="slate"
              value={kind}
              onChange={setKind}
              items={[
                { value: "easy", label: "Easy item" },
                { value: "hard", label: "Hard item" },
              ]}
            />
            <p className="board-note">
              {kind === "hard"
                ? "Each juror is more often wrong than right on this item. With independent jurors, adding more makes the wrong majority more likely, not less."
                : "Each juror is more often right than wrong on this item. With independent jurors, adding more makes the right majority more likely."}
            </p>
          </figcaption>
        </figure>
      </div>
    </header>
  );
}
