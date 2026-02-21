import { useState, useEffect, useRef } from 'react'

const CYCLE_MS = 4000 // 4s full cycle: 2s inhale, 2s exhale

/**
 * useBreathCycle
 * Returns live breath state synchronized to a 4-second cycle.
 *
 * { phase, progress, coherence, breathData }
 *   phase:     'inhale' | 'exhale'
 *   progress:  0–1 within current phase
 *   coherence: 0–1, rises gently as cycles accumulate (starts 0.5, caps 0.9)
 *   breathData: object passable to ΔE computation
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
      const cyclePos = (elapsed % CYCLE_MS) / CYCLE_MS

      const isInhale = cyclePos < 0.5
      const phaseProgress = isInhale ? cyclePos * 2 : (cyclePos - 0.5) * 2

      setPhase(isInhale ? 'inhale' : 'exhale')
      setProgress(phaseProgress)

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
