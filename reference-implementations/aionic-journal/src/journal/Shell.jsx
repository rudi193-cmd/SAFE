import { EntryCard } from './EntryCard'
import { ExportButton } from './ExportButton'

/**
 * Shell — sidebar entry list container.
 * Shows count + export button, empty state, EntryCard list.
 */
export function Shell({ entries, onDelete }) {
  return (
    <aside className="entry-sidebar">
      <div className="sidebar-label">
        <span>Entries ({entries.length})</span>
        <ExportButton entries={entries} />
      </div>
      {entries.length === 0 && (
        <p className="empty-state">Nothing yet. Write something.</p>
      )}
      {entries.map(e => (
        <EntryCard key={e.id} entry={e} onDelete={onDelete} />
      ))}
    </aside>
  )
}
