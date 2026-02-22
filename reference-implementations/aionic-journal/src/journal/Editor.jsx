export function Editor({ title, setTitle, body, setBody, tone, setTone, onSave, onKeyDown }) {
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
        onKeyDown={onKeyDown}
        rows={10}
      />
      <div className="editor-footer">
        <div className="tone-selector">
          {['reflective', 'grateful', 'processing', 'raw'].map(t => (
            <button
              key={t}
              className={'tone-btn ' + (tone === t ? 'active' : '')}
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
