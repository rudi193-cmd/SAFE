import { useState } from 'react'
import { saveAs } from 'file-saver'

/**
 * SessionEndButton -- explicit session close with export prompt.
 */
export function SessionEndButton({ entries }) {
  const [showModal, setShowModal] = useState(false)

  const handleExport = () => {
    const blob = new Blob(
      [JSON.stringify(entries, null, 2)],
      { type: 'application/json' }
    )
    const date = new Date().toISOString().split('T')[0]
    saveAs(blob, 'aionic-journal-' + date + '.json')
    setShowModal(false)
  }

  return (
    <>
      <button className="btn-session-end" onClick={() => setShowModal(true)}>
        End Session
      </button>
      {showModal && (
        <div className="draft-recovery-overlay">
          <div className="draft-recovery-card">
            <p className="draft-recovery-msg">Download a copy of this session?</p>
            <div className="draft-recovery-actions">
              <button className="btn-consent-yes" onClick={handleExport}>
                Download
              </button>
              <button className="btn-consent-no" onClick={() => setShowModal(false)}>
                Not now
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
