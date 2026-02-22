/**
 * Page2Consent — SAFE consent gateway.
 * Session-scoped permissions. User decides every time.
 */

const STREAMS = [
  {
    id: 'entries',
    label: 'Journal entries',
    description: 'Read and write your entries this session',
  },
  {
    id: 'export',
    label: 'Export to file',
    description: 'Download your entries as a file',
  },
]

export function Page2Consent({ onConsent, onDecline }) {
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
        <p className="consent-expiry">
          When you close this tab, all permissions expire. Tomorrow, it asks again.
        </p>
        <div className="consent-actions">
          <button className="btn-consent-yes" onClick={onConsent}>Yes, this session</button>
          <button className="btn-consent-no" onClick={onDecline}>No, local only</button>
        </div>
        <p className="consent-safe">SAFE — Session-Authorized, Fully Explicit</p>
      </div>
    </div>
  )
}
