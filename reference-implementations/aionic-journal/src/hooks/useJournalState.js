import { useState, useEffect } from 'react'
import { storeEntry, getAllEntries, deleteEntry } from '../services/storage'
import { useBreathCycle } from './useBreathCycle'
import { getBellMessage, getMode } from '../core/bell'

/**
 * useJournalState — all entry state and side effects.
 * Composes useBreathCycle and storage. Page3Journal assembles from this.
 */
export function useJournalState() {
  const [entries, setEntries] = useState([])
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [tone, setTone] = useState('reflective')
  const [deltaE, setDeltaE] = useState(-0.25)

  const { breathData } = useBreathCycle()
  const mode = getMode(deltaE)
  const bellMsg = getBellMessage(deltaE)

  const refresh = () => setEntries(getAllEntries())
  useEffect(() => { refresh() }, [])

  // Live ΔE: text length + breath coherence, centered at 0
  useEffect(() => {
    const lengthFactor = Math.min(body.length / 500, 1)
    const breathFactor = breathData?.coherence ?? 0.5
    setDeltaE((lengthFactor + breathFactor) / 2 - 0.5)
  }, [body, breathData?.coherence])

  const save = () => {
    if (!body.trim()) return
    storeEntry({ title, body, tone, deltaE })
    setTitle('')
    setBody('')
    refresh()
  }

  const remove = (id) => { deleteEntry(id); refresh() }

  return {
    entries,
    title, setTitle,
    body, setBody,
    tone, setTone,
    deltaE, mode, bellMsg,
    breathData,
    save, remove,
  }
}
