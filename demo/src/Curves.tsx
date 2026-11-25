// SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
// Accuracy and cost curves of EXP-002, drawn as hand-written SVG from the
// exported report table. Every point carries its seed-level t 95% interval;
// the strings shown are the strings the generated report prints.
import { useEffect, useMemo, useState } from "react";
import type { CellRef, CurvePoint, Results } from "./results";

const SERIES = [
  { rule: "MV", name: "Majority vote (MV)", cls: "s-mv", shape: "circle" },
  { rule: "SEQ", name: "Sequential public vote (SEQ)", cls: "s-seq", shape: "square" },
  { rule: "CW", name: "Confidence-weighted vote (CW, descriptive)", cls: "s-cw", shape: "triangle" },
] as const;

type Axis = "calls" | "cost";

function useNarrow(): boolean {
  const q = "(max-width: 40rem)";
  const [narrow, setNarrow] = useState(() => typeof window !== "undefined" && window.matchMedia(q).matches);
  useEffect(() => {
    const m = window.matchMedia(q);
    const on = () => setNarrow(m.matches);
    m.addEventListener("change", on);
    return () => m.removeEventListener("change", on);
  }, []);
  return narrow;
}

function niceTicks(lo: number, hi: number): number[] {
  const span = hi - lo;
  const step = [0.01, 0.02, 0.025, 0.05, 0.1, 0.2].find((s) => span / s <= 8) ?? 0.25;
  const out: number[] = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(Math.round(v * 1e6) / 1e6);
  return out;
}

function cost(p: CurvePoint, axis: Axis): number {
  return axis === "calls" ? p.budget : p.budget + p.messages_per_item;
}

function Marker({ shape, x, y, cls }: { shape: string; x: number; y: number; cls: string }) {
  if (shape === "circle") return <circle className={cls} cx={x} cy={y} r={4.5} />;
  if (shape === "square") return <rect className={cls} x={x - 4.2} y={y - 4.2} width={8.4} height={8.4} />;
  return <path className={cls} d={`M${x},${y - 5.5} L${x + 5.2},${y + 4} L${x - 5.2},${y + 4} Z`} />;
}

export function Curves({ r }: { r: Results }) {
  const [scenario, setScenario] = useState("S6");
  const [lam, setLam] = useState(0);
  const [axis, setAxis] = useState<Axis>("calls");
  const [tableOpen, setTableOpen] = useState(false);
  const narrow = useNarrow();
  // On narrow screens the drawing is laid out at its display size, so labels stay legible.
  const W = narrow ? 340 : 640;
  const H = narrow ? 320 : 380;
  const M = narrow ? { l: 60, r: 10, t: 14, b: 50 } : { l: 64, r: 16, t: 18, b: 56 };
  const lambdas = useMemo(() => [...new Set(r.curves.points.map((p) => p.lambda))].sort((a, b) => a - b), [r]);
  const sc = r.scenarios.find((s) => s.id === scenario)!;

  const pts = r.curves.points.filter((p) => p.scenario === scenario && p.lambda === lam);
  const single = pts.find((p) => p.rule === "SINGLE");
  const isRejected = (p: CurvePoint) =>
    r.holm_rejected.some((c: CellRef) => c.scenario === p.scenario && c.lambda === p.lambda && c.rule === p.rule && c.budget === p.budget);

  const series = SERIES.map((s) => ({ ...s, pts: pts.filter((p) => p.rule === s.rule).sort((a, b) => a.budget - b.budget) }));
  const all = series.flatMap((s) => s.pts);
  const yLo = Math.min(0, ...all.map((p) => p.ci_low));
  const yHi = Math.max(0, ...all.map((p) => p.ci_high));
  const pad = (yHi - yLo) * 0.08 || 0.01;
  const y0 = yLo - pad;
  const y1 = yHi + pad;
  const xs = all.map((p) => cost(p, axis));
  const xMax = Math.max(...xs);
  const lx = (v: number) => Math.log(v);
  const xPad = 0.06 * (lx(xMax) - lx(1));
  const X = (v: number) => M.l + ((lx(v) - lx(1) + xPad) / (lx(xMax) - lx(1) + 2 * xPad)) * (W - M.l - M.r);
  const Y = (v: number) => M.t + ((y1 - v) / (y1 - y0)) * (H - M.t - M.b);
  const xTicks = axis === "calls" ? [1, 3, 5, 9, 15, 31] : [...new Set(xs)].sort((a, b) => a - b);
  const yTicks = niceTicks(y0, y1);
  const offset = { MV: -7, SEQ: 0, CW: 7 } as Record<string, number>;

  const mv31 = series[0].pts.find((p) => p.budget === 31);
  const seq31 = series[1].pts.find((p) => p.budget === 31);
  const nRej = all.filter(isRejected).length;
  const describe =
    `${scenario} (${sc.homogeneous ? `homogeneous, p = ${sc.p_easy}` : `mixture: p_easy ${sc.p_easy}, hard share ${sc.h}, p_hard ${sc.p_hard}`}), lambda ${lam}. ` +
    `SINGLE accuracy ${single?.accuracy_display}. At 31 calls MV changes accuracy by ${mv31?.delta_display} [${mv31?.ci_low_display}, ${mv31?.ci_high_display}] ` +
    `and SEQ by ${seq31?.delta_display} [${seq31?.ci_low_display}, ${seq31?.ci_high_display}]. ` +
    (nRej > 0 ? `${nRej} of the cells shown are Holm-rejected (statistically detected degradation).` : "No cell shown is Holm-rejected.");

  return (
    <section id="curves" aria-labelledby="h-curves">
      <h2 id="h-curves">Accuracy and cost curves</h2>
      <p className="label label-measured">Measured, confirmatory: EXP-002, 30 seed-runs of 2000 items per point</p>
      <p>
        Each point is the change in accuracy against one reasoner making one call (the zero line), with its seed-level t 95%
        interval drawn as a vertical bar. Pick a scenario and a correlation level. Switch the horizontal axis to count the
        messages a sequential voter reads as cost, which is the secondary cost proxy of EXP-004.
      </p>
      <div className="controls" role="group" aria-label="Curve controls">
        <label>
          Scenario{" "}
          <select id="curve-scenario" value={scenario} onChange={(e) => setScenario(e.target.value)}>
            {r.scenarios.map((s) => (
              <option key={s.id} value={s.id}>
                {s.id}: {s.homogeneous ? `p ${s.p_easy}` : `p_easy ${s.p_easy}, h ${s.h}, p_hard ${s.p_hard}`}
              </option>
            ))}
          </select>
        </label>
        <label>
          Correlation lambda{" "}
          <select id="curve-lambda" value={lam} onChange={(e) => setLam(Number(e.target.value))}>
            {lambdas.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        </label>
        <div className="toggle" role="group" aria-label="Horizontal axis">
          <span className="toggle-title">Horizontal axis</span>
          <button type="button" id="axis-calls" aria-pressed={axis === "calls"} onClick={() => setAxis("calls")}>Calls per item</button>
          <button type="button" id="axis-cost" aria-pressed={axis === "cost"} onClick={() => setAxis("cost")}>Calls plus messages read</button>
        </div>
      </div>

      <figure className="chart">
        <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-labelledby="curve-title curve-desc">
          <title id="curve-title">Change in accuracy against SINGLE by {axis === "calls" ? "calls per item" : "calls plus messages read"}</title>
          <desc id="curve-desc">{describe}</desc>
          {yTicks.map((t) => (
            <g key={t}>
              <line className="grid" x1={M.l} x2={W - M.r} y1={Y(t)} y2={Y(t)} />
              <text className="tick" x={M.l - 8} y={Y(t) + 4} textAnchor="end">{t > 0 ? `+${t.toFixed(2)}` : t.toFixed(2)}</text>
            </g>
          ))}
          <line className="zero" x1={M.l} x2={W - M.r} y1={Y(0)} y2={Y(0)} />
          <text className="tick" x={W - M.r} y={Y(0) - 6} textAnchor="end">SINGLE, one call</text>
          {xTicks.map((t) => (
            <g key={t}>
              <line className="axis" x1={X(t)} x2={X(t)} y1={H - M.b} y2={H - M.b + 5} />
              <text className="tick" x={X(t)} y={H - M.b + 18} textAnchor="middle">{t}</text>
            </g>
          ))}
          <line className="axis" x1={M.l} x2={W - M.r} y1={H - M.b} y2={H - M.b} />
          <text className="axis-label" x={(M.l + W - M.r) / 2} y={H - 12} textAnchor="middle">
            {axis === "calls" ? "Calls per item, B (log scale)" : narrow ? "Calls plus messages read (log)" : "Calls plus messages read per item (log scale)"}
          </text>
          <text className="axis-label" transform={`translate(${narrow ? 12 : 16} ${(M.t + H - M.b) / 2}) rotate(-90)`} textAnchor="middle">
            {narrow ? "Change against SINGLE" : "Accuracy change against SINGLE"}
          </text>
          {series.map((s) => (
            <g key={s.rule}>
              <polyline
                className={`line ${s.cls}${s.rule === "CW" ? " dashed" : ""}`}
                points={s.pts.map((p) => `${X(cost(p, axis)) + offset[s.rule]},${Y(p.delta)}`).join(" ")}
              />
              {s.pts.map((p) => {
                const x = X(cost(p, axis)) + offset[s.rule];
                return (
                  <g key={p.budget}>
                    <line className={`bar ${s.cls}`} x1={x} x2={x} y1={Y(p.ci_low)} y2={Y(p.ci_high)} />
                    <line className={`bar ${s.cls}`} x1={x - 3} x2={x + 3} y1={Y(p.ci_low)} y2={Y(p.ci_low)} />
                    <line className={`bar ${s.cls}`} x1={x - 3} x2={x + 3} y1={Y(p.ci_high)} y2={Y(p.ci_high)} />
                    <Marker shape={s.shape} x={x} y={Y(p.delta)} cls={`mk ${s.cls}`} />
                    {isRejected(p) && <circle className="rej" cx={x} cy={Y(p.delta)} r={9} />}
                  </g>
                );
              })}
            </g>
          ))}
        </svg>
        <figcaption>
          <ul className="legend">
            {SERIES.map((s) => (
              <li key={s.rule}>
                <svg width="22" height="14" aria-hidden="true">
                  <line className={`line ${s.cls}${s.rule === "CW" ? " dashed" : ""}`} x1={1} x2={21} y1={7} y2={7} />
                  <Marker shape={s.shape} x={11} y={7} cls={`mk ${s.cls}`} />
                </svg>{" "}
                {s.name}
              </li>
            ))}
            <li>
              <svg width="22" height="18" aria-hidden="true"><circle className="rej" cx={11} cy={9} r={7} /></svg> Holm-rejected cell (degradation detected
              under the frozen rule)
            </li>
          </ul>
          <p className="chart-desc">{describe}</p>
          <p className="meta">
            Source: <code>{r.curves.source}</code>; {r.curves.interval}. CW is descriptive: its advantage follows from the assumed confidence
            model. At one call every rule is SINGLE, so its interval has zero width.
          </p>
        </figcaption>
      </figure>

      <details onToggle={(e) => setTableOpen(e.currentTarget.open)}>
        <summary>Table of the values in this chart</summary>
        {tableOpen && (
        <div className="table-scroll" id="t-curve" role="region" aria-label="Values of the accuracy curve" tabIndex={0}>
          <table>
            <thead>
              <tr>
                <th scope="col">Rule</th>
                <th scope="col">Calls</th>
                <th scope="col">Messages read</th>
                <th scope="col">Accuracy</th>
                <th scope="col">Change against SINGLE</th>
                <th scope="col">t 95% interval</th>
              </tr>
            </thead>
            <tbody>
              {series.flatMap((s) =>
                s.pts.map((p) => (
                  <tr key={s.rule + p.budget}>
                    <th scope="row">{p.rule}</th>
                    <td>{p.budget}</td>
                    <td>{p.messages_per_item}</td>
                    <td>{p.accuracy_display}</td>
                    <td>{p.delta_display}{isRejected(p) ? " (Holm-rejected)" : ""}</td>
                    <td>[{p.ci_low_display}, {p.ci_high_display}]</td>
                  </tr>
                )),
              )}
            </tbody>
          </table>
        </div>
        )}
      </details>
    </section>
  );
}
