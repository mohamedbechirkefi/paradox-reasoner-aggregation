// SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
// Messages and constants shared by the sandbox page and its Web Worker.
import type { ScenarioParams } from "./engine";

export const SANDBOX_BUDGETS = [1, 3, 5, 9, 15, 31];
export const DETAIL_ITEMS = 24;

export interface SandboxParams {
  scenario: ScenarioParams;
  lam: number;
  w: number;
  nItems: number;
  seed: number;
}

export interface ItemDetail {
  y: number;
  hard: number;
  pItem: number;
  leaderCorrect: number;
  adopt: number[];
  correct: number[];
  seqKey: number[];
  herdU: number[];
  tieCoin: number;
}

export interface SandboxResult {
  params: SandboxParams;
  rows: { budget: number; single: number; mv: number; seq: number }[];
  items: ItemDetail[];
  ms: number;
}

export type WorkerRequest = { type: "run"; params: SandboxParams };
export type WorkerReply = { type: "progress"; stage: string } | { type: "done"; result: SandboxResult } | { type: "error"; message: string };

