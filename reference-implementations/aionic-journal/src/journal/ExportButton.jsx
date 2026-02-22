import { saveAs } from 'file-saver'

/**
 * ExportButton — download entries as a dated JSON file.
 * Fulfils the "Export to file" consent stream from Page2Consent.
 * Hidden when there are no entries.
 */
export function ExportButton({ entries }) {
  if (entries.length === 0) return null

  const handleExport = () => {
    const blob = new Blob(
      [JSON.stringify(entries, null, 2)],
      { type: 'application/json' }
    )
    const date = new Date().toISOString().split('T')[0]
    saveAs(blob, `aionic-journal-${date}.json`)
  }

  return (
    <button
      className="btn-export"
      onClick={handleExport}
      title="Export entries to file"
    >
      ↓
    </button>
  )
}
