/**
 * Editor — text input pane.
 * Title, body textarea, tone selector, Save button.
 */
export function Editor({ title, setTitle, body, setBody, tone, setTone, onSave }) {
  return (
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
        <button className="btn-save" onClick={onSave} disabled={!body.trim()}>
          Save
        </button>
      </div>
    </main>
  )
}
