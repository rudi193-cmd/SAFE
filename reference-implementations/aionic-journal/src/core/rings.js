/**
 * core/rings.js — Breath phase timing constants and helpers.
 * Distinct from continuity/rings.js (three-ring storage architecture).
 */

export const INHALE_MS = 2000
export const EXHALE_MS = 2000
export const CYCLE_MS  = INHALE_MS + EXHALE_MS  // 4000ms total

export function getPhase(cyclePos) {
  return cyclePos < 0.5 ? 'inhale' : 'exhale'
}

export function getPhaseProgress(cyclePos) {
  return cyclePos < 0.5
    ? cyclePos * 2
    : (cyclePos - 0.5) * 2
}
