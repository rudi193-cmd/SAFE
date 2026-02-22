import { useState, useEffect, useRef, useCallback } from 'react'
import { storeEntry, getAllEntries, deleteEntry, saveDraft, getDraft, clearDraft } from '../services/storage'
import { useBreathCycle } from './useBreathCycle'
import { useEditorSession } from './useEditorSession'
import { getBellMessage, getMode } from '../core/bell'
import { computeDeltaE } from '../core/deltaE'
import { getConfidence } from '../core/confidence'
import { generateSessionId, sessionTimer } from '../core/session'

export function useJournalState() {
  const [entries, setEntries] = useState([])
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [tone, setTone] = useState('reflective')
  const [deltaE, setDeltaE] = useState(-0.25)
  const [hasDraft, setHasDraft] = useState(false)
  const [draftRecovered, setDraftRecovered] = useState(false)
  const [recoveryChoice, setRecoveryChoice] = useState(null)

  const captureSession = useRef(generateSessionId())
  const timer = useRef(sessionTimer())

  const { breathData } = useBreathCycle()
  const mode = getMode(deltaE)
  const bellMsg = getBellMessage(deltaE)
  const { onKeyDown, recordToneChange, getSessionMeta } = useEditorSession(timer.current)

  const refresh = async () => {
    const all = await getAllEntries()
    setEntries(all)
  }

  useEffect(() => { refresh() }, [])

  useEffect(() => {
    const draft = getDraft()
    if (draft) setHasDraft(true)
  }, [])

  useEffect(() => {
    setDeltaE(computeDeltaE(body, breathData))
  }, [body, breathData?.coherence])

  useEffect(() => {
    if (!body) return
    const t = setTimeout(() => saveDraft(body), 500)
    return () => clearTimeout(t)
  }, [body])

  const recoverDraft = useCallback((choice) => {
    const draft = getDraft()
    setHasDraft(false)
    setRecoveryChoice(choice)
    if (choice === 'review') {
      setBody(draft)
      setDraftRecovered(true)
    } else if (choice === 'save') {
      storeEntry({
        title: '',
        content: draft,
        tone: 'raw',
        deltaE: -0.25,
        confidence: 'low',
        capture_session: captureSession.current,
        session_meta: { draft_recovered: true, recovery_choice: 'save' },
      }).then(refresh)
      clearDraft()
    } else {
      clearDraft()
    }
  }, [])

  const setToneTracked = useCallback((t) => {
    recordToneChange()
    setTone(t)
  }, [recordToneChange])

  const save = async () => {
    if (!body.trim()) return
    const meta = getSessionMeta({
      wordCount: body.trim().split(/\s+/).length,
      coherence: breathData?.coherence ?? 0.5,
      titleFilled: !!title.trim(),
      draftRecovered,
      recoveryChoice,
    })
    await storeEntry({
      title,
      content: body,
      tone,
      deltaE,
      confidence: getConfidence(deltaE),
      capture_session: captureSession.current,
      session_meta: meta,
    })
    setTitle('')
    setBody('')
    setDraftRecovered(false)
    setRecoveryChoice(null)
    clearDraft()
    await refresh()
  }

  const remove = async (id) => {
    await deleteEntry(id)
    await refresh()
  }

  return {
    entries,
    title, setTitle,
    body, setBody,
    tone, setTone: setToneTracked,
    deltaE, mode, bellMsg,
    breathData,
    onKeyDown,
    hasDraft, recoverDraft,
    save, remove,
  }
}
