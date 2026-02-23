/**
 * BreathRing — Visual breathing indicator.
 * 5-phase: inhale expands, hold stays full, exhale contracts,
 *          hold_out stays contracted, rest stays contracted (dimmed).
 * Border color adapts to ΔE mode: calm (blue), neutral (gray), uplift (gold).
 */
export function BreathRing({ breathData, mode = 'neutral' }) {
  const { phase = 'inhale', progress = 0 } = breathData || {}

  // Scale: inhale 1.0→1.35, hold 1.35, exhale 1.35→1.0, hold_out/rest 1.0
  let scale
  if (phase === 'inhale')    scale = 1.0 + progress * 0.35
  else if (phase === 'hold') scale = 1.35
  else if (phase === 'exhale') scale = 1.35 - progress * 0.35
  else scale = 1.0  // hold_out, rest

  const modeColor = {
    calm:    '#4a90b8',
    neutral: '#7a7a72',
    uplift:  '#d4a843',
  }[mode] ?? '#7a7a72'

  // Dim during rest phase
  const opacity = phase === 'rest' ? 0.4 + progress * 0.6 : 1.0
  const glowSize = Math.round(scale * 8)

  const label = {
    inhale:   'Inhale...',
    hold:     'Hold...',
    exhale:   'Exhale...',
    hold_out: 'Hold...',
    rest:     '',
  }[phase] ?? ''

  return (
    <div
      className="breath-ring-wrap"
      title={label}
      aria-label="Breath indicator"
    >
      <div
        className="breath-ring"
        style={{
          transform: `scale(${scale.toFixed(3)})`,
          borderColor: modeColor,
          boxShadow: `0 0 ${glowSize}px ${modeColor}55`,
          opacity: opacity.toFixed(3),
        }}
      />
    </div>
  )
}
