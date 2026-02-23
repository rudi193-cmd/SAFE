import { useState, useEffect, useRef } from 'react'
import { CYCLE_MS, getPhaseInfo } from '../core/rings'

/**
 * useBreathCycle
 * Returns live breath state synchronized to the 17-second 5-phase cycle:
 * inhale 3s / hold 3s / exhale 4s / hold-out 4s / rest 3s
 *
 * { phase, progress, coherence, breathData }
 *   phase:     'inhale' | 'hold' | 'exhale' | 'hold_out' | 'rest'
 *   progress:  0–1 within current phase
 *   coherence: 0–1, rises gently as cycles accumulate (starts 0.5, caps 0.9)
 */
export function useBreathCycle() {
  const [phase, setPhase] = useState('inhale')
  const [progress, setProgress] = useState(0)
  const [coherence, setCoherence] = useState(0.5)
  const startRef = useRef(Date.now())
  const cycleCountRef = useRef(0)

  useEffect(() => {
    let raf

    const tick = () => {
      const elapsed = Date.now() - startRef.current
      const { name, progress: prog } = getPhaseInfo(elapsed)

      setPhase(name)
      setProgress(prog)

      const completedCycles = Math.floor(elapsed / CYCLE_MS)
      if (completedCycles > cycleCountRef.current) {
        cycleCountRef.current = completedCycles
        setCoherence(c => Math.min(0.9, c + 0.04))
      }

      raf = requestAnimationFrame(tick)
    }

    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])

  const breathData = { phase, progress, coherence }
  return { phase, progress, coherence, breathData }
}
