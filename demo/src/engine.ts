// SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
// Browser port of the research engine's draw table and of the SINGLE, MV and
// SEQ rules (src/paradox/generator.py and src/paradox/rules.py). It ports
// NumPy's SeedSequence, its spawn() and the PCG64 generator with
// Generator.random(), so for the same scenario, lambda, w, item count and run
// seed it reproduces the Python engine's draws and decisions exactly. CW is not
// ported: it needs NumPy's ziggurat normal sampler. The confidence stream is
// independent of the streams used here, so omitting it changes no other draw.
// The equality is checked by src/engine.test.ts against a fixture written by
// scripts/export_sandbox_fixture.py from the Python engine.

const M32 = 0xffffffff;
const MASK64 = (1n << 64n) - 1n;
const MASK128 = (1n << 128n) - 1n;
const PCG_MULT = 0x2360ed051fc65da44385df649fccf645n;

// NumPy SeedSequence constants (numpy/random/bit_generator.pyx).
const INIT_A = 0x43b0d7e5;
const MULT_A = 0x931e8875;
const INIT_B = 0x8b51f9dd;
const MULT_B = 0x58f38ded;
const MIX_MULT_L = 0xca01f9dd;
const MIX_MULT_R = 0x4973f715;
const POOL_SIZE = 4;

/** Words of a non-negative integer, least significant 32 bits first (NumPy's _coerce_to_uint32_array). */
function uint32Words(x: number): number[] {
  if (!Number.isSafeInteger(x) || x < 0) throw new Error("seed must be a non-negative safe integer");
  if (x === 0) return [0];
  const out: number[] = [];
  let v = BigInt(x);
  while (v > 0n) {
    out.push(Number(v & 0xffffffffn));
    v >>= 32n;
  }
  return out;
}

/** Pool of SeedSequence(entropy, spawn_key) with the default pool size. */
export function seedSequencePool(entropy: number, spawnKey: number[]): number[] {
  const run = uint32Words(entropy);
  const spawn = spawnKey.flatMap(uint32Words);
  if (spawn.length > 0) while (run.length < POOL_SIZE) run.push(0);
  const ent = [...run, ...spawn];
  let hc = INIT_A;
  const hashmix = (value: number): number => {
    value = (value ^ hc) >>> 0;
    hc = Math.imul(hc, MULT_A) >>> 0;
    value = Math.imul(value, hc) >>> 0;
    return (value ^ (value >>> 16)) >>> 0;
  };
  const mix = (x: number, y: number): number => {
    const r = (Math.imul(MIX_MULT_L, x) - Math.imul(MIX_MULT_R, y)) >>> 0;
    return (r ^ (r >>> 16)) >>> 0;
  };
  const mixer = new Array<number>(POOL_SIZE);
  for (let i = 0; i < POOL_SIZE; i++) mixer[i] = hashmix(i < ent.length ? ent[i] : 0);
  for (let s = 0; s < POOL_SIZE; s++) {
    for (let d = 0; d < POOL_SIZE; d++) if (s !== d) mixer[d] = mix(mixer[d], hashmix(mixer[s]));
  }
  for (let s = POOL_SIZE; s < ent.length; s++) {
    for (let d = 0; d < POOL_SIZE; d++) mixer[d] = mix(mixer[d], hashmix(ent[s]));
  }
  return mixer;
}

/** SeedSequence.generate_state(nWords, np.uint64), as BigInts. */
export function generateState64(pool: number[], nWords: number): bigint[] {
  let hc = INIT_B;
  const w32: number[] = [];
  for (let i = 0; i < 2 * nWords; i++) {
    let v = (pool[i % pool.length] ^ hc) >>> 0;
    hc = Math.imul(hc, MULT_B) >>> 0;
    v = Math.imul(v, hc) >>> 0;
    w32.push((v ^ (v >>> 16)) >>> 0);
  }
  const out: bigint[] = [];
  for (let i = 0; i < nWords; i++) out.push((BigInt(w32[2 * i + 1]) << 32n) | BigInt(w32[2 * i]));
  return out;
}

/** NumPy's PCG64 (XSL-RR 128/64) with Generator.random() doubles. */
export class Pcg64 {
  private state = 0n;
  private inc = 0n;

  constructor(pool: number[]) {
    const v = generateState64(pool, 4);
    const initState = (v[0] << 64n) | v[1];
    const initSeq = (v[2] << 64n) | v[3];
    this.inc = ((initSeq << 1n) | 1n) & MASK128;
    this.state = 0n;
    this.step();
    this.state = (this.state + initState) & MASK128;
    this.step();
  }

  private step(): void {
    this.state = (this.state * PCG_MULT + this.inc) & MASK128;
  }

  nextUint64(): bigint {
    this.step();
    const s = this.state;
    const x = ((s >> 64n) ^ s) & MASK64;
    const rot = s >> 122n;
    return ((x >> rot) | (x << ((64n - rot) & 63n))) & MASK64;
  }

  /** Uniform double in [0, 1), as numpy.random.Generator.random(). */
  random(): number {
    return Number(this.nextUint64() >> 11n) * (1.0 / 9007199254740992.0);
  }
}

/** Child generators of SeedSequence(seed).spawn(10), one per named stream. */
const STREAMS = ["labels", "difficulty", "leader", "adopt", "private", "signal", "seq_order", "herd", "delib", "tie"] as const;
type StreamName = (typeof STREAMS)[number];

export function streamRng(seed: number, name: StreamName): Pcg64 {
  return new Pcg64(seedSequencePool(seed, [STREAMS.indexOf(name)]));
}

export const MAX_REASONERS = 31;
export const MAX_ITEMS = 5000;

export interface ScenarioParams {
  p_easy: number;
  h: number;
  p_hard: number;
}

export interface Draws {
  nItems: number;
  y: Uint8Array;
  hard: Uint8Array;
  pItem: Float64Array;
  leaderCorrect: Uint8Array;
  adopt: Uint8Array; // (I, 31), row-major
  correct: Uint8Array; // (I, 31)
  seqKey: Float64Array; // (I, 31)
  herdU: Float64Array; // (I, 31)
  tieCoin: Uint8Array;
}

function checkProb(name: string, x: number): void {
  if (!Number.isFinite(x) || x < 0 || x > 1) throw new Error(`${name} must be in [0, 1]`);
}

/** Port of generate_run() without the confidence and DELIB streams. */
export function generateDraws(sc: ScenarioParams, lam: number, nItems: number, seed: number): Draws {
  checkProb("p_easy", sc.p_easy);
  checkProb("h", sc.h);
  checkProb("p_hard", sc.p_hard);
  checkProb("lambda", lam);
  if (!Number.isInteger(nItems) || nItems < 1 || nItems > MAX_ITEMS) throw new Error(`items must be an integer from 1 to ${MAX_ITEMS}`);
  if (!Number.isInteger(seed) || seed < 0 || seed > M32) throw new Error("seed must be an integer from 0 to 4294967295");
  const I = nItems;
  const J = MAX_REASONERS;
  const pHard = sc.h > 0 ? sc.p_hard : sc.p_easy;

  const y = new Uint8Array(I);
  let g = streamRng(seed, "labels");
  for (let i = 0; i < I; i++) y[i] = g.random() < 0.5 ? 1 : 0;

  const hard = new Uint8Array(I);
  const pItem = new Float64Array(I);
  g = streamRng(seed, "difficulty");
  for (let i = 0; i < I; i++) {
    hard[i] = g.random() < sc.h ? 1 : 0;
    pItem[i] = hard[i] ? pHard : sc.p_easy;
  }

  const leaderCorrect = new Uint8Array(I);
  g = streamRng(seed, "leader");
  for (let i = 0; i < I; i++) leaderCorrect[i] = g.random() < pItem[i] ? 1 : 0;

  const adopt = new Uint8Array(I * J);
  g = streamRng(seed, "adopt");
  for (let k = 0; k < I * J; k++) adopt[k] = g.random() < lam ? 1 : 0;

  const correct = new Uint8Array(I * J);
  g = streamRng(seed, "private");
  for (let i = 0; i < I; i++) {
    for (let j = 0; j < J; j++) {
      const k = i * J + j;
      const priv = g.random() < pItem[i] ? 1 : 0;
      correct[k] = adopt[k] ? leaderCorrect[i] : priv;
    }
  }

  const seqKey = new Float64Array(I * J);
  g = streamRng(seed, "seq_order");
  for (let k = 0; k < I * J; k++) seqKey[k] = g.random();

  const herdU = new Float64Array(I * J);
  g = streamRng(seed, "herd");
  for (let k = 0; k < I * J; k++) herdU[k] = g.random();

  const tieCoin = new Uint8Array(I);
  g = streamRng(seed, "tie");
  for (let i = 0; i < I; i++) tieCoin[i] = g.random() < 0.5 ? 1 : 0;

  return { nItems: I, y, hard, pItem, leaderCorrect, adopt, correct, seqKey, herdU, tieCoin };
}

function checkN(n: number): void {
  if (!Number.isInteger(n) || n < 1 || n > MAX_REASONERS) throw new Error(`budget must be an integer from 1 to ${MAX_REASONERS}`);
}

function decide(k: number, n: number, coin: number): number {
  return 2 * k === n ? coin : 2 * k > n ? 1 : 0;
}

/** Speaking order of reasoners 0..n-1 for item i (stable argsort of seq_key). */
export function seqOrder(d: Draws, i: number, n: number): number[] {
  const J = MAX_REASONERS;
  const idx = Array.from({ length: n }, (_, j) => j);
  return idx.sort((a, b) => d.seqKey[i * J + a] - d.seqKey[i * J + b] || a - b);
}

export interface SeqItem {
  order: number[];
  /** Public vote of reasoner j (1 = correct), indexed by reasoner. */
  votes: number[];
  /** True if reasoner j followed the strict leader of the earlier tally. */
  herded: boolean[];
}

/** SEQ public votes for one item (port of sequential_votes()). */
export function seqItem(d: Draws, i: number, n: number, w: number): SeqItem {
  checkN(n);
  checkProb("w", w);
  const J = MAX_REASONERS;
  const order = seqOrder(d, i, n);
  const votes = new Array<number>(n).fill(0);
  const herded = new Array<boolean>(n).fill(false);
  let lead = 0;
  for (const j of order) {
    const priv = d.correct[i * J + j];
    const herd = d.herdU[i * J + j] < w;
    let vote = priv;
    if (herd && lead > 0) vote = 1;
    else if (herd && lead < 0) vote = 0;
    herded[j] = herd && lead !== 0;
    votes[j] = vote;
    lead += vote ? 1 : -1;
  }
  return { order, votes, herded };
}

export interface RuleSummary {
  /** Number of items each rule decided correctly. */
  single: number;
  mv: number;
  seq: number;
}

/** Correct-decision counts of SINGLE, MV and SEQ at budget n over all items. */
export function summarize(d: Draws, n: number, w: number): RuleSummary {
  checkN(n);
  const J = MAX_REASONERS;
  let single = 0;
  let mv = 0;
  let seq = 0;
  for (let i = 0; i < d.nItems; i++) {
    single += d.correct[i * J];
    let k = 0;
    for (let j = 0; j < n; j++) k += d.correct[i * J + j];
    mv += decide(k, n, d.tieCoin[i]);
    const s = seqItem(d, i, n, w);
    let ks = 0;
    for (const v of s.votes) ks += v;
    seq += decide(ks, n, d.tieCoin[i]);
  }
  return { single, mv, seq };
}
