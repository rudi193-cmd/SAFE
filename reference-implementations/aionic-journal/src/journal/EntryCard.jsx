import { useState } from 'react'

/**
 * EntryCard — individual journal entry.
 * Click to expand body. Delete button visible when expanded.
 */
export function EntryCard({ entry, onDelete }) {
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
