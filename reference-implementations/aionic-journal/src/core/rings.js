/**
 * core/rings.js — Breath phase timing constants and helpers.
 * Distinct from continuity/rings.js (three-ring storage architecture).
 *
 * 5-phase cycle: inhale 3s / hold 3s / exhale 4s / hold-out 4s / rest 3s = 17s
 * This is the system heartbeat — all Willow/SAFE timing syncs to this cycle.
 */

export const PHASES = [
  { name: 'inhale',   ms: 3000 },
  { name: 'hold',     ms: 3000 },
  { name: 'exhale',   ms: 4000 },
  { name: 'hold_out', ms: 4000 },
  { name: 'rest',     ms: 3000 },
]

export const CYCLE_MS = PHASES.reduce((sum, p) => sum + p.ms, 0)  // 17000ms

export function getPhaseInfo(elapsedMs) {
  const pos = elapsedMs % CYCLE_MS
  let acc = 0
  for (const phase of PHASES) {
    if (pos < acc + phase.ms) {
      return { name: phase.name, progress: (pos - acc) / phase.ms }
    }
    acc += phase.ms
  }
  return { name: 'rest', progress: 1 }
}
