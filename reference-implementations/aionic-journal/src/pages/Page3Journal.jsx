import { useState, useEffect } from 'react'
import { storeEntry, getAllEntries, deleteEntry } from '../services/storage'
import { useBreathCycle } from '../hooks/useBreathCycle'
import { getBellMessage, getMode } from '../core/bell'
import { BreathRing } from '../ui/BreathRing'

function EntryCard({ entry, onDelete }) {
  const [expanded, setExpanded] = useState(false)
  const date = new Date(entry.created_at).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
  return (
    <div className="entry-card" onClick={() => setExpanded(!expanded)}>
      <div className="entry-header">
        <span className="entry-date">{date}</span>
        {entry.tone && (
          <span className={`entry-tone tone-${entry.tone}`}>{entry.tone}</span>
        )}
      </div>
      {entry.title && <div className="entry-title">{entry.title}</div>}
      <div className={`entry-body ${expanded ? 'expanded' : 'collapsed'}`}>
        {entry.body}
      </div>
      {expanded && (
        <button
          className="btn-delete"
          onClick={e => { e.stopPropagation(); onDelete(entry.id) }}
        >
          Delete
        </button>
      )}
    </div>
  )
}

/**
 * Page3Journal — Main journaling view.
 * Uses localStorage persistence via services/storage.
 * ΔE computed live from text length + breath coherence.
 */
export function Page3Journal({ consented }) {
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

  return (
    <div className={`journal-app mode-${mode}`}>
      <header className="app-header">
        <span className="app-wordmark">Jane</span>
        <BreathRing breathData={breathData} mode={mode} />
        <span className="bell-message">{bellMsg}</span>
        {!consented && <span className="session-notice">local only</span>}
      </header>
      <div className="journal-layout">
        <aside className="entry-sidebar">
          <div className="sidebar-label">Entries ({entries.length})</div>
          {entries.length === 0 && (
            <p className="empty-state">Nothing yet. Write something.</p>
          )}
          {entries.map(e => (
            <EntryCard key={e.id} entry={e} onDelete={remove} />
          ))}
        </aside>
        <main className="editor-pane">
          <input
            className="editor-title"
            placeholder="Title (optional)"
            value={title}
            onChange={e => setTitle(e.target.value)}
          />
          <textarea
            className="editor-body"
            placeholder="What happened. What you noticed. What you are carrying."
            value={body}
            onChange={e => setBody(e.target.value)}
            rows={10}
          />
          <div className="editor-footer">
            <div className="tone-selector">
              {['reflective', 'grateful', 'processing', 'raw'].map(t => (
                <button
                  key={t}
                  className={`tone-btn ${tone === t ? 'active' : ''}`}
                  onClick={() => setTone(t)}
                >
                  {t}
                </button>
              ))}
            </div>
            <button className="btn-save" onClick={save} disabled={!body.trim()}>
              Save
            </button>
          </div>
        </main>
      </div>
    </div>
  )
}
