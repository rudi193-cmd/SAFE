/**
 * Bell messages — emotional gateway cues.
 * Maps ΔE to adaptive mode and guided prompt.
 */

export function getMode(deltaE) {
  if (deltaE < -0.3) return 'calm'
  if (deltaE > 0.3) return 'uplift'
  return 'neutral'
}

export function getBellMessage(deltaE) {
  if (deltaE < -0.3) return 'Breathe...'
  if (deltaE > 0.3) return "You're flowing..."
  return 'Write what emerges...'
}
