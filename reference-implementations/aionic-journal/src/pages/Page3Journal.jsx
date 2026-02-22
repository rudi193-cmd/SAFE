import { useJournalState } from '../hooks/useJournalState'
import { Shell } from '../journal/Shell'
import { Editor } from '../journal/Editor'
import { BreathRing } from '../ui/BreathRing'

/**
 * Page3Journal — main journaling view.
 * Assembles Shell + Editor via useJournalState. No local state.
 */
export function Page3Journal({ consented }) {
  const {
    entries,
    title, setTitle,
    body, setBody,
    tone, setTone,
    mode, bellMsg, breathData,
    save, remove,
  } = useJournalState()

  return (
    <div className={`journal-app mode-${mode}`}>
      <header className="app-header">
        <span className="app-wordmark">Jane</span>
        <BreathRing breathData={breathData} mode={mode} />
        <span className="bell-message">{bellMsg}</span>
        {!consented && <span className="session-notice">local only</span>}
      </header>
      <div className="journal-layout">
        <Shell entries={entries} onDelete={remove} />
        <Editor
          title={title} setTitle={setTitle}
          body={body} setBody={setBody}
          tone={tone} setTone={setTone}
          onSave={save}
        />
      </div>
    </div>
  )
}
