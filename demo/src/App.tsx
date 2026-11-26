// SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
import { useEffect, useState } from "react";
import { Curves } from "./Curves";
import { fmtEstimate, fmtInterval, loadResults, ResultsError, type Experiment, type Results } from "./results";
import { Sandbox } from "./Sandbox";

type State = { kind: "loading" } | { kind: "error"; message: string } | { kind: "ready"; results: Results };

export function App() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    loadResults()
      .then((results) => setState({ kind: "ready", results }))
      .catch((e: unknown) =>
        setState({ kind: "error", message: e instanceof ResultsError ? e.message : "results could not be loaded" }),
      );
  }, []);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <header className="site">
        <div className="wrap">
          <p className="kicker">PARADOX, a preregistered simulation study of synthetic reasoners</p>
          <h1>When more reasoners make worse decisions</h1>
          <p className="lede">Under an equal compute budget, when does aggregating fallible reasoners improve or degrade accuracy?</p>
          <nav aria-label="Sections">
            <a href="#overview">Overview</a>
            <a href="#curves">Curves</a>
            <a href="#results">Results</a>
            <a href="#sandbox">Network and sandbox</a>
            <a href="#assumptions">Assumptions</a>
            <a href="#method">Method and limitations</a>
          </nav>
        </div>
      </header>
      <main id="main" className="wrap">
        {state.kind === "loading" && <p role="status">Loading the published results.</p>}
        {state.kind === "error" && (
          <div role="alert" className="panel error">
            <h2>Results unavailable</h2>
            <p>The published results file failed validation, so no numbers and no sandbox are shown.</p>
            <p><code>{state.message}</code></p>
          </div>
        )}
        {state.kind === "ready" && <Page r={state.results} />}
      </main>
      <footer className="site">
        <div className="wrap">
          <p>
            Runs offline after the first load. No data about visitors is collected, stored or sent anywhere; the sandbox runs in your browser
            and keeps nothing. Synthetic reasoners are not language models or people.
          </p>
          <p>Mohamed Bechir Kefi, independent researcher.</p>
        </div>
      </footer>
    </>
  );
}

function kindLabel(e: Experiment): { cls: string; text: string } {
  if (e.status.startsWith("exploratory")) return { cls: "label-exploratory", text: "Measured, exploratory" };
  return { cls: "label-measured", text: "Measured, confirmatory" };
}

function find(r: Results, id: string, label: string) {
  const e = r.experiments.find((x) => x.id === id);
  return e?.estimates.find((x) => x.label === label);
}

function Page({ r }: { r: Results }) {
  const head = find(r, "EXP-002", "S6, lambda 0, MV, B = 31");
  const confirm = r.experiments.filter((e) => e.id.startsWith("EXP-"));
  return (
    <>
      <section id="overview" aria-labelledby="h-overview">
        <h2 id="h-overview">Overview</h2>
        <p className="status-label"><strong>Status.</strong> {r.status_label}</p>
        <p>
          Each item is a binary decision. A budget of B calls buys B votes from synthetic reasoners whose errors can be correlated and whose
          items differ in difficulty. Three rules spend that budget: majority vote (MV), confidence-weighted vote (CW) and sequential public
          voting with herding (SEQ). Each is compared with one reasoner making one call (SINGLE).
          {head && (
            <>
              {" "}The largest loss is MV in scenario S6 at 31 calls: {fmtEstimate(head)} accuracy, seed-level t 95% interval {fmtInterval(head)}.
            </>
          )}
        </p>
        <ul className="verdicts">
          {confirm.map((e) => (
            <li key={e.id}>
              <strong>{e.id}</strong> {e.title}: {e.verdict}
            </li>
          ))}
        </ul>
        <div className="key" role="group" aria-label="How results are labelled">
          <p className="label label-measured">Measured, confirmatory: frozen protocol, committed results</p>
          <p className="label label-exploratory">Measured, exploratory: after the verdicts; changes no verdict</p>
          <p className="label label-sandbox">Sandbox output: your settings, your browser</p>
          <p className="label label-assumption">Assumption: a model parameter chosen by design</p>
        </div>
      </section>

      <Curves r={r} />

      <section id="results" aria-labelledby="h-results">
        <h2 id="h-results">Published results</h2>
        <p className="note">
          These numbers come from the committed results produced at code revision <code>{r.code_revision.slice(0, 12)}</code>; they are the
          numbers the manuscript prints. Confirmatory, null, disconfirmed and exploratory results are shown in the same format. They are
          separate from anything the sandbox produces.
        </p>
        {r.experiments.map((e) => {
          const k = kindLabel(e);
          return (
            <article key={e.id} className="panel" aria-labelledby={`h-${e.id}`}>
              <h3 id={`h-${e.id}`}>
                {e.id}: {e.title}
              </h3>
              <p className={`label ${k.cls}`}>{k.text}</p>
              <p>
                <span className="badge">{e.status}</span> <strong>Verdict under the frozen rule:</strong> {e.verdict}
              </p>
              {e.estimates.length > 0 && (
                <div className="table-scroll" id={`t-${e.id}`} role="region" aria-label={`${e.id} estimates`} tabIndex={0}>
                  <table>
                    <thead>
                      <tr>
                        <th scope="col">Quantity</th>
                        <th scope="col">Estimate</th>
                        <th scope="col">Interval (95%)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {e.estimates.map((x) => (
                        <tr key={x.label}>
                          <th scope="row">{x.label}</th>
                          <td className="num">{fmtEstimate(x)}</td>
                          <td className="num">{fmtInterval(x)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              {e.notes.map((n, i) => (
                <p key={i} className="note">{n}</p>
              ))}
              <p className="meta">
                Report: <code>{e.report_path}</code>
                {e.claim_ids.length > 0 && <> · Claims: {e.claim_ids.join(", ")}</>}
              </p>
            </article>
          );
        })}
      </section>

      <Sandbox r={r} />

      <section id="assumptions" aria-labelledby="h-assumptions">
        <h2 id="h-assumptions">Assumptions</h2>
        <p className="label label-assumption">Assumption: design values of the frozen EXP-002 configuration, not estimates of any population</p>
        <dl className="assumptions">
          {r.assumptions.map((a) => (
            <div key={a.name}>
              <dt>{a.name}</dt>
              <dd>
                {a.value} <span className="meta">({a.source})</span>
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <section id="method" aria-labelledby="h-method">
        <h2 id="h-method">Method and limitations</h2>
        <p>
          Four experiments were preregistered and frozen by the owner on 2026-11-24 before any confirmatory run. EXP-001 validates the engine
          against closed forms; EXP-002 maps 240 rule-by-cell contrasts with paired, seed-level intervals and Holm control; EXP-003 compares
          four dependence models at matched competence and pairwise correlation; EXP-004 checks robustness to secondary choices. The seed-run
          is the independent unit, and the 30 seeds are shared across cells, so cells are paired but not independent.
        </p>
        <h3>Limitations (manuscript section 7)</h3>
        <ul>
          {r.limitations.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
        <details>
          <summary>Strings not printed verbatim in the manuscript</summary>
          <ul className="meta">
            {r.display_exceptions.map((x) => (
              <li key={x.text}>
                <code>{x.text}</code>: {x.note} Source: <code>{x.source}</code>
              </li>
            ))}
          </ul>
        </details>
        <details>
          <summary>Source files and hashes</summary>
          <ul className="meta">
            {r.sources.map((s) => (
              <li key={s.path}>
                <code>{s.path}</code> <code>{s.sha256.slice(0, 12)}</code>
              </li>
            ))}
          </ul>
        </details>
      </section>
    </>
  );
}
