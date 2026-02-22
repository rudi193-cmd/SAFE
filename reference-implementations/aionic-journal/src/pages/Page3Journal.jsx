import { useJournalState } from '../hooks/useJournalState'
import { Shell } from '../journal/Shell'
import { Editor } from '../journal/Editor'
import { BreathRing } from '../ui/BreathRing'
import { SessionEndButton } from '../journal/SessionEndButton'

export function Page3Journal({ consented }) {
  const {
    entries, title, setTitle, body, setBody,
    tone, setTone, mode, bellMsg, breathData,
    onKeyDown, hasDraft, recoverDraft, save, remove,
  } = useJournalState()

  return (
    <div className={'journal-app mode-' + mode}>
      {hasDraft && (
        <div className="draft-recovery-overlay">
          <div className="draft-recovery-card">
            <p className="draft-recovery-msg">
              You have unsaved thoughts from a previous session.
            </p>
            <div className="draft-recovery-actions">
              <button className="btn-consent-yes" onClick={() => recoverDraft('review')}>
                Review them
              </button>
              <button className="btn-consent-no" onClick={() => recoverDraft('save')}>
                Save without reviewing
              </button>
              <button className="btn-draft-discard" onClick={() => recoverDraft('discard')}>
                Discard
              </button>
            </div>
          </div>
        </div>
      )}
      <header className="app-header">
        <span className="app-wordmark">Jane</span>
        <BreathRing breathData={breathData} mode={mode} />
        <span className="bell-message">{bellMsg}</span>
        {!consented && <span className="session-notice">local only</span>}
        <SessionEndButton entries={entries} />
      </header>
      <div className="journal-layout">
        <Shell entries={entries} onDelete={remove} />
        <Editor
          title={title} setTitle={setTitle}
          body={body} setBody={setBody}
          tone={tone} setTone={setTone}
          onSave={save}
          onKeyDown={onKeyDown}
        />
      </div>
    </div>
  )
}
