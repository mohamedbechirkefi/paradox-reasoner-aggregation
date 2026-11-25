// SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
// Visitor sandbox: runs the browser port of the research engine in a Web
// Worker. Its output is labelled as sandbox output and never mixed with the
// published results. Nothing is stored or sent anywhere.
import { useCallback, useEffect, useRef, useState, type ChangeEvent } from "react";
import { MAX_ITEMS } from "./engine";
import { Network } from "./Network";
import type { Results } from "./results";
import { DETAIL_ITEMS, type SandboxParams, type SandboxResult, type WorkerReply, type WorkerRequest } from "./sandboxTypes";

interface Form {
  scenarioId: string;
  p_easy: number;
  h: number;
  p_hard: number;
  lam: number;
  w: number;
  nItems: number;
  seed: number;
}

function clamp(x: number, lo: number, hi: number, fallback: number): number {
  return Number.isFinite(x) ? Math.min(hi, Math.max(lo, x)) : fallback;
}

function fmt4(x: number): string {
  return x.toFixed(4);
}

function signed(x: number): string {
  return (x >= 0 ? "+" : "") + x.toFixed(4);
}

export function Sandbox({ r }: { r: Results }) {
  const s6 = r.scenarios.find((s) => s.id === "S6") ?? r.scenarios[0];
  const firstSeed = r.sandbox.confirmatory_seeds_first[0];
  const defaults: Form = { scenarioId: s6.id, p_easy: s6.p_easy, h: s6.h, p_hard: s6.p_hard, lam: 0.5, w: 0.5, nItems: 2000, seed: firstSeed };
  const [form, setForm] = useState<Form>(defaults);
  const [running, setRunning] = useState(false);
  const [out, setOut] = useState("");
  const [result, setResult] = useState<SandboxResult | null>(null);
  const [item, setItem] = useState(0);
  const [netB, setNetB] = useState(15);
  const [mode, setMode] = useState<"MV" | "SEQ">("MV");
  const worker = useRef<Worker | null>(null);

  const spawn = useCallback(() => {
    worker.current?.terminate();
    const w = new Worker(new URL("./sandbox.worker.ts", import.meta.url), { type: "module" });
    w.onmessage = (ev: MessageEvent<WorkerReply>) => {
      const m = ev.data;
      if (m.type === "progress") return;
      setRunning(false);
      if (m.type === "error") {
        setOut(`The sandbox rejected these settings: ${m.message}`);
        return;
      }
      const res = m.result;
      const at31 = res.rows.find((x) => x.budget === 31)!;
      const n = res.params.nItems;
      setResult(res);
      setItem(0);
      setOut(
        `Sandbox output (seed ${res.params.seed}, ${n} items, lambda ${res.params.lam}, w ${res.params.w}): at 31 calls MV is ` +
          `${fmt4(at31.mv / n)} and SEQ ${fmt4(at31.seq / n)} against SINGLE ${fmt4(at31.single / n)}. One seed-run, no interval.`,
      );
    };
    worker.current = w;
  }, []);

  useEffect(() => {
    spawn();
    return () => worker.current?.terminate();
  }, [spawn]);

  const run = (f: Form = form) => {
    const params: SandboxParams = {
      scenario: { p_easy: f.p_easy, h: f.h, p_hard: f.p_hard },
      lam: f.lam,
      w: f.w,
      nItems: f.nItems,
      seed: f.seed,
    };
    setRunning(true);
    setOut("");
    worker.current?.postMessage({ type: "run", params } satisfies WorkerRequest);
  };

  // A first run on load, so the network has something to show.
  const started = useRef(false);
  useEffect(() => {
    if (started.current) return;
    started.current = true;
    run(defaults);
  }, []);

  const cancel = () => {
    spawn(); // terminating the worker is the cancellation; no partial output is kept
    setRunning(false);
    setOut("Sandbox run cancelled; the previous output, if any, is still shown below.");
  };

  const reset = () => {
    setForm(defaults);
    setNetB(15);
    setMode("MV");
    run(defaults);
  };

  const pickScenario = (id: string) => {
    const s = r.scenarios.find((x) => x.id === id);
    setForm((f) => (s ? { ...f, scenarioId: id, p_easy: s.p_easy, h: s.h, p_hard: s.p_hard } : { ...f, scenarioId: "custom" }));
  };

  const num = (k: keyof Form, lo: number, hi: number, integer = false) => (e: ChangeEvent<HTMLInputElement>) => {
    const raw = Number(e.target.value);
    const v = clamp(integer ? Math.round(raw) : raw, lo, hi, lo);
    setForm((f) => ({ ...f, [k]: v, ...(k === "p_easy" || k === "h" || k === "p_hard" ? { scenarioId: "custom" } : {}) }));
  };

  const save = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify({ label: "sandbox output, not a research result", engine: r.sandbox.port_of, ...result }, null, 1)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `paradox-sandbox-seed${result.params.seed}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const p = result?.params;
  const matchesPublished =
    p !== undefined &&
    p.nItems === 2000 &&
    p.w === 0.5 &&
    r.sandbox.confirmatory_seeds_first.includes(p.seed) &&
    r.scenarios.some((s) => s.p_easy === p.scenario.p_easy && s.h === p.scenario.h && s.p_hard === p.scenario.p_hard) &&
    [0, 0.25, 0.5, 0.75].includes(p.lam);

  return (
    <section id="sandbox" aria-labelledby="h-sandbox" className="sandbox">
      <h2 id="h-sandbox">Reasoning network and sandbox</h2>
      <p className="label label-sandbox">Sandbox output: computed in your browser from your settings; not a research result</p>
      <p>
        The sandbox runs a port of the research engine (SINGLE, MV and SEQ) in a background worker. For the same scenario, correlation,
        herding probability, item count and seed it reproduces the Python engine's draws and decisions exactly; a unit test checks this
        against a fixture from the Python engine and against one committed EXP-002 seed-run. CW is not ported. A sandbox run is one
        seed-run, so it carries no interval and must not be compared with the 30-seed published means above.
      </p>
      <div className="controls" role="group" aria-label="Sandbox settings">
        <label>
          Scenario{" "}
          <select id="sb-scenario" value={form.scenarioId} onChange={(e) => pickScenario(e.target.value)}>
            {r.scenarios.map((s) => (
              <option key={s.id} value={s.id}>{s.id}</option>
            ))}
            <option value="custom">custom</option>
          </select>
        </label>
        <label>p_easy <input type="number" min={0} max={1} step={0.05} id="sb-p_easy" value={form.p_easy} onChange={num("p_easy", 0, 1)} /></label>
        <label>hard share h <input type="number" min={0} max={1} step={0.05} id="sb-h" value={form.h} onChange={num("h", 0, 1)} /></label>
        <label>p_hard <input type="number" min={0} max={1} step={0.05} id="sb-p_hard" value={form.p_hard} onChange={num("p_hard", 0, 1)} /></label>
        <label>Correlation lambda <input type="number" min={0} max={1} step={0.05} id="sb-lam" value={form.lam} onChange={num("lam", 0, 1)} /></label>
        <label>Herding w <input type="number" min={0} max={1} step={0.05} id="sb-w" value={form.w} onChange={num("w", 0, 1)} /></label>
        <label>Items <input type="number" min={1} max={MAX_ITEMS} step={100} id="sb-nItems" value={form.nItems} onChange={num("nItems", 1, MAX_ITEMS, true)} /></label>
        <label>Seed <input type="number" min={0} max={4294967295} id="sb-seed" value={form.seed} onChange={num("seed", 0, 4294967295, true)} /></label>
      </div>
      <div className="controls">
        <button type="button" id="sb-run" onClick={() => run()} disabled={running}>Run sandbox</button>
        <button type="button" id="sb-cancel" onClick={cancel} disabled={!running}>Cancel</button>
        <button type="button" id="sb-reset" onClick={reset}>Reset to defaults</button>
        <button type="button" id="sb-save" onClick={save} disabled={!result}>Save output as JSON</button>
      </div>
      <p className="meta">
        Bounds: at most {MAX_ITEMS} items and 31 reasoners per run. Default seed {firstSeed} is the first confirmatory seed; with an EXP-002
        scenario and lambda, w 0.5 and 2000 items, the output equals that one seed-run of EXP-002.
      </p>
      <p aria-live="polite" className="sandbox-out">{out}</p>
      {running && <p role="status">Sandbox running.</p>}

      {result && (
        <>
          {matchesPublished && (
            <p className="note">These settings reproduce one committed EXP-002 seed-run; the published numbers are means over 30 such runs.</p>
          )}
          <div className="table-scroll" id="t-sandbox" role="region" aria-label="Sandbox accuracy by budget" tabIndex={0}>
            <table>
              <caption>Sandbox output, one seed-run of {result.params.nItems} items (no interval). Accuracy of MV and SEQ by calls B and change against SINGLE, whose accuracy is {fmt4(result.rows[0].single / result.params.nItems)} at every B.</caption>
              <thead>
                <tr>
                  <th scope="col">B</th>
                  <th scope="col">MV</th>
                  <th scope="col">SEQ</th>
                  <th scope="col">MV change</th>
                  <th scope="col">SEQ change</th>
                </tr>
              </thead>
              <tbody>
                {result.rows.map((x) => {
                  const n = result.params.nItems;
                  return (
                    <tr key={x.budget}>
                      <th scope="row">{x.budget}</th>
                      <td>{fmt4(x.mv / n)}</td>
                      <td>{fmt4(x.seq / n)}</td>
                      <td>{signed((x.mv - x.single) / n)}</td>
                      <td>{signed((x.seq - x.single) / n)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <h3>Reasoning network for one item</h3>
          <p>
            Each ring node is a reasoner; the centre is the shared answer of the common-shock model. Lines show which reasoners adopted it,
            so a wrong shared answer propagates to every adopter. In sequential mode the ring follows the speaking order and a double ring
            marks a reasoner that copied the leader of the earlier votes.
          </p>
          <div className="controls" role="group" aria-label="Network view">
            <label>
              Item{" "}
              <input
                id="net-item"
                type="number"
                min={1}
                max={Math.min(DETAIL_ITEMS, result.items.length)}
                value={item + 1}
                onChange={(e) => setItem(clamp(Math.round(Number(e.target.value)) - 1, 0, Math.min(DETAIL_ITEMS, result.items.length) - 1, 0))}
              />
            </label>
            <label>
              Reasoners shown (B){" "}
              <input id="net-b" type="number" min={1} max={31} value={netB} onChange={(e) => setNetB(clamp(Math.round(Number(e.target.value)), 1, 31, 15))} />
            </label>
            <div className="toggle" role="group" aria-label="Votes shown">
              <span className="toggle-title">Votes shown</span>
              <button type="button" id="net-mv" aria-pressed={mode === "MV"} onClick={() => setMode("MV")}>Answers (MV)</button>
              <button type="button" id="net-seq" aria-pressed={mode === "SEQ"} onClick={() => setMode("SEQ")}>Sequential public votes (SEQ)</button>
            </div>
          </div>
          <Network item={result.items[item]} n={netB} w={result.params.w} mode={mode} index={item} />
        </>
      )}
    </section>
  );
}
