/**
 * confidence.js -- derives confidence_level from deltaE.
 * Mirrors confidence_level enum from oral_stories schema.
 */
export function getConfidence(deltaE) {
  if (deltaE > 0.3) return 'high'
  if (deltaE > -0.3) return 'medium'
  return 'low'
}
