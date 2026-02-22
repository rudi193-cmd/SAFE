/**
 * core/deltaE.js — App-level ΔE per journal_app_2025-11.md spec.
 * Simpler than continuity/deltaE.js — centered at 0 for mode thresholds.
 *
 * Formula: (lengthFactor + breathFactor) / 2 - 0.5
 * Range:   -0.5 (empty + no coherence)  →  +0.5 (500+ chars + full sync)
 */
export function computeDeltaE(entryText, breathData) {
  const lengthFactor = Math.min(entryText.length / 500, 1)
  const breathFactor = breathData?.coherence ?? 0.5
  return (lengthFactor + breathFactor) / 2 - 0.5
}
