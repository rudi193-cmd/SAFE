import { EntryCard } from './EntryCard'

/**
 * Shell — sidebar entry list container.
 * Shows count, empty state, and EntryCard list.
 */
export function Shell({ entries, onDelete }) {
  return (
    <aside className="entry-sidebar">
      <div className="sidebar-label">Entries ({entries.length})</div>
      {entries.length === 0 && (
        <p className="empty-state">Nothing yet. Write something.</p>
      )}
      {entries.map(e => (
        <EntryCard key={e.id} entry={e} onDelete={onDelete} />
      ))}
    </aside>
  )
}
