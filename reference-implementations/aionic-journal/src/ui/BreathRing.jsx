/**
 * BreathRing — Visual breathing indicator.
 * Expands on inhale, contracts on exhale.
 * Border color adapts to ΔE mode: calm (blue), neutral (gray), uplift (gold).
 */
export function BreathRing({ breathData, mode = 'neutral' }) {
  const { phase = 'inhale', progress = 0 } = breathData || {}

  // Scale 1.0 → 1.35 on inhale, 1.35 → 1.0 on exhale
  const scale = phase === 'inhale'
    ? 1.0 + progress * 0.35
    : 1.35 - progress * 0.35

  const modeColor = {
    calm:    '#4a90b8',
    neutral: '#7a7a72',
    uplift:  '#d4a843',
  }[mode] ?? '#7a7a72'

  const glowSize = Math.round(progress * 10)

  return (
    <div
      className="breath-ring-wrap"
      title={phase === 'inhale' ? 'Inhale...' : 'Exhale...'}
      aria-label="Breath indicator"
    >
      <div
        className="breath-ring"
        style={{
          transform: `scale(${scale.toFixed(3)})`,
          borderColor: modeColor,
          boxShadow: `0 0 ${glowSize}px ${modeColor}55`,
        }}
      />
    </div>
  )
}
