// SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
// Published results: loaded from public/data/results.json, which
// scripts/export_demo_data.py writes from committed results only.
// Validation fails closed: any missing or malformed field means no numbers are shown.

export const SCHEMA = "lab-demo-results";
export const SCHEMA_MAJOR = 1;

export interface Estimate {
  label: string;
  estimate: number;
  ci_low: number | null;
  ci_high: number | null;
  ci_level: number | null;
  unit: string;
  /** Exact text the manuscript prints for the estimate and interval; shown verbatim when present. */
  display: string | null;
  interval_display: string | null;
}

export interface Experiment {
  id: string;
  title: string;
  status: string;
  verdict: string;
  estimates: Estimate[];
  claim_ids: string[];
  report_path: string;
  notes: string[];
}

export interface Assumption {
  name: string;
  value: string;
  source: string;
}

export interface Source {
  path: string;
  sha256: string;
}

/** One EXP-002 cell from the generated report table (results/EXP-002/report.md). */
export interface CurvePoint {
  scenario: string;
  lambda: number;
  lambda_display: string;
  rule: string;
  budget: number;
  messages_per_item: number;
  n_seeds: number;
  accuracy: number;
  accuracy_display: string;
  delta: number;
  delta_display: string;
  ci_low: number;
  ci_high: number;
  ci_low_display: string;
  ci_high_display: string;
}

export interface Curves {
  source: string;
  experiment: string;
  interval: string;
  points: CurvePoint[];
}

export interface ScenarioDef {
  id: string;
  p_easy: number;
  h: number;
  p_hard: number;
  mu: number;
  homogeneous: boolean;
}

export interface CellRef {
  scenario: string;
  lambda: number;
  rule: string;
  budget: number;
}

export interface DisplayException {
  text: string;
  source: string;
  note: string;
}

export interface SandboxInfo {
  port_of: string;
  rules: string[];
  not_ported: string;
  fixture: string;
  tolerance: string;
  confirmatory_seeds_first: number[];
}

export interface Results {
  schema: string;
  schema_version: string;
  project: string;
  question: string;
  status_label: string;
  code_revision: string;
  sources: Source[];
  experiments: Experiment[];
  assumptions: Assumption[];
  limitations: string[];
  curves: Curves;
  scenarios: ScenarioDef[];
  holm_rejected: CellRef[];
  display_exceptions: DisplayException[];
  sandbox: SandboxInfo;
}

export class ResultsError extends Error {}

type Obj = Record<string, unknown>;

function obj(v: unknown, where: string): Obj {
  if (typeof v !== "object" || v === null || Array.isArray(v)) {
    throw new ResultsError(`${where}: expected an object`);
  }
  return v as Obj;
}

function str(o: Obj, k: string, where: string): string {
  const v = o[k];
  if (typeof v !== "string" || v.length === 0) {
    throw new ResultsError(`${where}.${k}: expected a non-empty string`);
  }
  return v;
}

function num(o: Obj, k: string, where: string, nullable = false): number | null {
  const v = o[k];
  if (nullable && v === null) return null;
  if (typeof v !== "number" || !Number.isFinite(v)) {
    throw new ResultsError(`${where}.${k}: expected a finite number`);
  }
  return v;
}

function arr(o: Obj, k: string, where: string): unknown[] {
  const v = o[k];
  if (!Array.isArray(v)) throw new ResultsError(`${where}.${k}: expected an array`);
  return v;
}

function strArr(o: Obj, k: string, where: string): string[] {
  return arr(o, k, where).map((v, i) => {
    if (typeof v !== "string") throw new ResultsError(`${where}.${k}[${i}]: expected a string`);
    return v;
  });
}

function estimate(v: unknown, where: string): Estimate {
  const o = obj(v, where);
  const e: Estimate = {
    label: str(o, "label", where),
    estimate: num(o, "estimate", where) as number,
    ci_low: num(o, "ci_low", where, true),
    ci_high: num(o, "ci_high", where, true),
    ci_level: num(o, "ci_level", where, true),
    unit: typeof o.unit === "string" ? o.unit : "",
    display: typeof o.display === "string" ? o.display : null,
    interval_display: typeof o.interval_display === "string" ? o.interval_display : null,
  };
  if ((e.ci_low === null) !== (e.ci_high === null)) {
    throw new ResultsError(`${where}: interval must have both bounds or neither`);
  }
  if (e.ci_low !== null && e.ci_high !== null && e.ci_low > e.ci_high) {
    throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  }
  return e;
}

function bool(o: Obj, k: string, where: string): boolean {
  const v = o[k];
  if (typeof v !== "boolean") throw new ResultsError(`${where}.${k}: expected a boolean`);
  return v;
}

function prob(o: Obj, k: string, where: string): number {
  const v = num(o, k, where) as number;
  if (v < 0 || v > 1) throw new ResultsError(`${where}.${k}: expected a value in [0, 1]`);
  return v;
}

function int(o: Obj, k: string, where: string, min: number, max: number): number {
  const v = num(o, k, where) as number;
  if (!Number.isInteger(v) || v < min || v > max) throw new ResultsError(`${where}.${k}: expected an integer from ${min} to ${max}`);
  return v;
}

const RULES = new Set(["SINGLE", "MV", "SEQ", "CW"]);

function curvePoint(v: unknown, where: string): CurvePoint {
  const o = obj(v, where);
  const p: CurvePoint = {
    scenario: str(o, "scenario", where),
    lambda: prob(o, "lambda", where),
    lambda_display: str(o, "lambda_display", where),
    rule: str(o, "rule", where),
    budget: int(o, "budget", where, 1, 31),
    messages_per_item: int(o, "messages_per_item", where, 0, 1_000_000),
    n_seeds: int(o, "n_seeds", where, 1, 1000),
    accuracy: prob(o, "accuracy", where),
    accuracy_display: str(o, "accuracy_display", where),
    delta: num(o, "delta", where) as number,
    delta_display: str(o, "delta_display", where),
    ci_low: num(o, "ci_low", where) as number,
    ci_high: num(o, "ci_high", where) as number,
    ci_low_display: str(o, "ci_low_display", where),
    ci_high_display: str(o, "ci_high_display", where),
  };
  if (!RULES.has(p.rule)) throw new ResultsError(`${where}.rule: unknown rule ${p.rule}`);
  if (p.ci_low > p.ci_high) throw new ResultsError(`${where}: ci_low exceeds ci_high`);
  if (p.delta < p.ci_low - 1e-9 || p.delta > p.ci_high + 1e-9) throw new ResultsError(`${where}: delta outside its interval`);
  for (const [n, d] of [[p.accuracy, p.accuracy_display], [p.delta, p.delta_display], [p.ci_low, p.ci_low_display], [p.ci_high, p.ci_high_display]] as const) {
    if (Math.abs(Number(d) - n) > 1e-12) throw new ResultsError(`${where}: display text ${d} does not match its value`);
  }
  return p;
}

function curves(v: unknown): Curves {
  const o = obj(v, "curves");
  const points = arr(o, "points", "curves").map((x, i) => curvePoint(x, `curves.points[${i}]`));
  if (points.length === 0) throw new ResultsError("curves.points: empty");
  return { source: str(o, "source", "curves"), experiment: str(o, "experiment", "curves"), interval: str(o, "interval", "curves"), points };
}

function scenario(v: unknown, where: string): ScenarioDef {
  const o = obj(v, where);
  return {
    id: str(o, "id", where),
    p_easy: prob(o, "p_easy", where),
    h: prob(o, "h", where),
    p_hard: prob(o, "p_hard", where),
    mu: prob(o, "mu", where),
    homogeneous: bool(o, "homogeneous", where),
  };
}

function cellRef(v: unknown, where: string): CellRef {
  const o = obj(v, where);
  return { scenario: str(o, "scenario", where), lambda: prob(o, "lambda", where), rule: str(o, "rule", where), budget: int(o, "budget", where, 1, 31) };
}

function sandboxInfo(v: unknown): SandboxInfo {
  const o = obj(v, "sandbox");
  const seeds = arr(o, "confirmatory_seeds_first", "sandbox").map((x, i) => {
    if (typeof x !== "number" || !Number.isInteger(x) || x < 0 || x > 0xffffffff) throw new ResultsError(`sandbox.confirmatory_seeds_first[${i}]: expected a uint32`);
    return x;
  });
  if (seeds.length === 0) throw new ResultsError("sandbox.confirmatory_seeds_first: empty");
  return {
    port_of: str(o, "port_of", "sandbox"),
    rules: strArr(o, "rules", "sandbox"),
    not_ported: str(o, "not_ported", "sandbox"),
    fixture: str(o, "fixture", "sandbox"),
    tolerance: str(o, "tolerance", "sandbox"),
    confirmatory_seeds_first: seeds,
  };
}

export function validateResults(raw: unknown): Results {
  const o = obj(raw, "results");
  if (o.schema !== SCHEMA) throw new ResultsError(`results.schema: expected "${SCHEMA}"`);
  const version = str(o, "schema_version", "results");
  if (Number(version.split(".")[0]) !== SCHEMA_MAJOR) {
    throw new ResultsError(`results.schema_version: unsupported major version ${version}`);
  }
  const experiments = arr(o, "experiments", "results").map((v, i) => {
    const w = `experiments[${i}]`;
    const e = obj(v, w);
    return {
      id: str(e, "id", w),
      title: str(e, "title", w),
      status: str(e, "status", w),
      verdict: str(e, "verdict", w),
      estimates: arr(e, "estimates", w).map((x, j) => estimate(x, `${w}.estimates[${j}]`)),
      claim_ids: strArr(e, "claim_ids", w),
      report_path: str(e, "report_path", w),
      notes: strArr(e, "notes", w),
    };
  });
  if (experiments.length === 0) throw new ResultsError("results.experiments: empty");
  return {
    schema: SCHEMA,
    schema_version: version,
    project: str(o, "project", "results"),
    question: str(o, "question", "results"),
    status_label: str(o, "status_label", "results"),
    code_revision: str(o, "code_revision", "results"),
    sources: arr(o, "sources", "results").map((v, i) => {
      const s = obj(v, `sources[${i}]`);
      const sha = str(s, "sha256", `sources[${i}]`);
      if (!/^[0-9a-f]{64}$/.test(sha)) throw new ResultsError(`sources[${i}].sha256: not a sha256`);
      return { path: str(s, "path", `sources[${i}]`), sha256: sha };
    }),
    experiments,
    assumptions: arr(o, "assumptions", "results").map((v, i) => {
      const a = obj(v, `assumptions[${i}]`);
      return {
        name: str(a, "name", `assumptions[${i}]`),
        value: str(a, "value", `assumptions[${i}]`),
        source: str(a, "source", `assumptions[${i}]`),
      };
    }),
    limitations: strArr(o, "limitations", "results"),
    ...extensions(o),
  };
}

function extensions(o: Obj) {
  const scenarios = arr(o, "scenarios", "results").map((v, i) => scenario(v, `scenarios[${i}]`));
  if (scenarios.length === 0) throw new ResultsError("results.scenarios: empty");
  const c = curves(o.curves);
  const ids = new Set(scenarios.map((s) => s.id));
  for (const p of c.points) if (!ids.has(p.scenario)) throw new ResultsError(`curves: unknown scenario ${p.scenario}`);
  return {
    curves: c,
    scenarios,
    holm_rejected: arr(o, "holm_rejected", "results").map((v, i) => cellRef(v, `holm_rejected[${i}]`)),
    display_exceptions: arr(o, "display_exceptions", "results").map((v, i) => {
      const w = `display_exceptions[${i}]`;
      const e = obj(v, w);
      return { text: str(e, "text", w), source: str(e, "source", w), note: str(e, "note", w) };
    }),
    sandbox: sandboxInfo(o.sandbox),
  };
}

export async function loadResults(url = "./data/results.json"): Promise<Results> {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new ResultsError(`could not load ${url} (HTTP ${res.status})`);
  let raw: unknown;
  try {
    raw = await res.json();
  } catch {
    throw new ResultsError(`${url} is not valid JSON`);
  }
  return validateResults(raw);
}

/** Formats a number for display without inventing precision. */
export function fmt(x: number, digits = 3): string {
  if (Number.isInteger(x)) return x.toString();
  return Number(x.toPrecision(digits)).toString();
}

export function fmtEstimate(e: Estimate, digits = 3): string {
  return e.display ?? `${fmt(e.estimate, digits)}${e.unit ? " " + e.unit : ""}`;
}

export function fmtInterval(e: Estimate, digits = 3): string {
  if (e.interval_display !== null) return e.interval_display;
  if (e.ci_low === null || e.ci_high === null) return "none";
  const level = e.ci_level === null ? "" : `${Math.round(e.ci_level * 100)}% `;
  return `${level}[${fmt(e.ci_low, digits)}, ${fmt(e.ci_high, digits)}]`;
}
