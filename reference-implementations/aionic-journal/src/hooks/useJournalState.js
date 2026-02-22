import { useState, useEffect } from 'react'
import { storeEntry, getAllEntries, deleteEntry } from '../services/storage'
import { useBreathCycle } from './useBreathCycle'
import { getBellMessage, getMode } from '../core/bell'
import { computeDeltaE } from '../core/deltaE'

/**
 * useJournalState — all entry state and side effects.
 * Async throughout (Dexie storage). Page3Journal assembles from this.
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

  const refresh = async () => {
    const all = await getAllEntries()
    setEntries(all)
  }
  useEffect(() => { refresh() }, [])

  useEffect(() => {
    setDeltaE(computeDeltaE(body, breathData))
  }, [body, breathData?.coherence])

  const save = async () => {
    if (!body.trim()) return
    await storeEntry({ title, body, tone, deltaE })
    setTitle('')
    setBody('')
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
    tone, setTone,
    deltaE, mode, bellMsg,
    breathData,
    save, remove,
  }
}
