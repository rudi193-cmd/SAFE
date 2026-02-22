import { useRef, useCallback } from 'react'

/**
 * useEditorSession -- instruments editor keystrokes for 17D behavioral signals.
 * Returns: { onKeyDown, recordToneChange, getSessionMeta }
 */
export function useEditorSession(timer) {
  const statsRef = useRef({
    totalKeys: 0,
    backspaces: 0,
    editKeys: 0,
    toneChanges: 0,
    keystampsMs: [],
  })

  const onKeyDown = useCallback((e) => {
    const s = statsRef.current
    s.totalKeys++
    const now = Date.now()
    s.keystampsMs.push(now)
    const cutoff = now - 60_000
    s.keystampsMs = s.keystampsMs.filter(t => t > cutoff)
    if (e.key === 'Backspace' || e.key === 'Delete') s.backspaces++
    if (e.key.length > 1 && e.key !== 'Backspace' && e.key !== 'Delete') s.editKeys++
  }, [])

  const recordToneChange = useCallback(() => {
    statsRef.current.toneChanges++
  }, [])

  const getSessionMeta = useCallback((opts = {}) => {
    const s = statsRef.current
    const durationS = timer?.elapsed() ?? 0
    const wpmAvg = s.totalKeys > 0 && durationS > 0
      ? Math.round((s.totalKeys / 5) / (durationS / 60))
      : 0
    const backspaceRatio = s.totalKeys > 0
      ? Math.round((s.backspaces / s.totalKeys) * 100) / 100
      : 0
    return {
      session_duration_s:  durationS,
      word_count_final:    opts.wordCount ?? 0,
      wpm_avg:             wpmAvg,
      edit_count:          s.editKeys,
      backspace_ratio:     backspaceRatio,
      coherence_at_save:   opts.coherence ?? 0.5,
      title_filled:        opts.titleFilled ?? false,
      tone_changes:        s.toneChanges,
      draft_recovered:     opts.draftRecovered ?? false,
      recovery_choice:     opts.recoveryChoice ?? null,
    }
  }, [timer])

  return { onKeyDown, recordToneChange, getSessionMeta }
}
