import { useState, useEffect } from 'react'
import { storeEntry, getAllEntries, deleteEntry } from './continuity/rings.js'
import { calculateCoherence } from './continuity/coherence.js'
import { computeDeltaE, classifyState } from './continuity/deltaE.js'

const STREAMS = [
  { id: 'entries', label: 'Journal entries', description: 'Read and write your entries this session' },
  { id: 'export', label: 'Export to file', description: 'Download your entries as a file' },
]

function ConsentScreen({ onConsent, onDecline }) {
  return (
    <div className="consent-overlay">
      <div className="consent-card">
        <div className="consent-logo">Jane</div>
        <p className="consent-tagline">Aionic Journal</p>
        <p className="consent-intro">Before this session begins, may I access:</p>
        <ul className="consent-streams">
          {STREAMS.map(s => (
            <li key={s.id}>
              <strong>{s.label}</strong>
              <span>{s.description}</span>
            </li>
          ))}
        </ul>
        <p className="consent-expiry">When you close this tab, all permissions expire. Tomorrow, it asks again.</p>
        <div className="consent-actions">
          <button className="btn-consent-yes" onClick={onConsent}>Yes, this session</button>
          <button className="btn-consent-no" onClick={onDecline}>No, local only</button>
        </div>
        <p className="consent-safe">SAFE — Session-Authorized, Fully Explicit</p>
      </div>
    </div>
  )
}

function DeltaBadge({ state }) {
  const labels = { regenerative: '↑ ΔE+', stable: '· ΔE=', decaying: '↓ ΔE−' }
  return <span className={`delta-badge delta-${state}`}>{labels[state] || '· ΔE='}</span>
}

function EntryCard({ entry, onDelete }) {
  const [expanded, setExpanded] = useState(false)
  const date = new Date(entry.created_at).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })
  return (
    <div className="entry-card" onClick={() => setExpanded(!expanded)}>
      <div className="entry-header">
        <span className="entry-date">{date}</span>
        {entry.tone && <span className={`entry-tone tone-${entry.tone}`}>{entry.tone}</span>}
      </div>
      {entry.title && <div className="entry-title">{entry.title}</div>}
      <div className={`entry-body ${expanded ? 'expanded' : 'collapsed'}`}>{entry.body}</div>
      {expanded && (
        <button className="btn-delete" onClick={e => { e.stopPropagation(); onDelete(entry.id) }}>
          Delete
        </button>
      )}
    </div>
  )
}

function JournalApp({ consented }) {
  const [entries, setEntries] = useState([])
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [tone, setTone] = useState('reflective')
  const [deltaState, setDeltaState] = useState('stable')
  const [prevCI, setPrevCI] = useState({ C: 0.6, t: Date.now() })

  const refresh = () => setEntries(getAllEntries())
  useEffect(() => { refresh() }, [])

  const save = () => {
    if (!body.trim()) return
    const recent = getAllEntries().slice(0, 5)
    const ci = calculateCoherence({ title, body, tone }, recent)
    const now = { C: ci, t: Date.now() }
    const dE = computeDeltaE({ Cprev: prevCI.C, tPrev: prevCI.t, Cnow: now.C, tNow: now.t })
    setPrevCI(now)
    setDeltaState(classifyState(dE))
    storeEntry({ title, body, tone, ci })
    setTitle('')
    setBody('')
    refresh()
  }

  const remove = (id) => { deleteEntry(id); refresh() }

  return (
    <div className="journal-app">
      <header className="app-header">
        <span className="app-wordmark">Jane</span>
        <DeltaBadge state={deltaState} />
        {!consented && <span className="session-notice">local only · no persistence</span>}
      </header>
      <div className="journal-layout">
        <aside className="entry-sidebar">
          <div className="sidebar-label">Entries ({entries.length})</div>
          {entries.length === 0 && <p className="empty-state">Nothing yet. Write something.</p>}
          {entries.map(e => <EntryCard key={e.id} entry={e} onDelete={remove} />)}
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
            placeholder="What happened. What you noticed. What you're carrying."
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
                >{t}</button>
              ))}
            </div>
            <button className="btn-save" onClick={save} disabled={!body.trim()}>Save</button>
          </div>
        </main>
      </div>
    </div>
  )
}

export default function App() {
  const [consent, setConsent] = useState(null)
  if (consent === null) {
    return <ConsentScreen onConsent={() => setConsent(true)} onDecline={() => setConsent(false)} />
  }
  return <JournalApp consented={consent} />
}
