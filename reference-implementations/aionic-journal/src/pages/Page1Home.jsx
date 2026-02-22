/**
 * Page1Home — Welcome screen.
 * Single action: Begin → moves to consent.
 */
export function Page1Home({ onBegin }) {
  return (
    <div className="page-home">
      <div className="home-card">
        <div className="home-wordmark">Jane</div>
        <p className="home-tagline">Aionic Journal</p>
        <p className="home-description">
          Breath-synchronized journaling.<br />
          Write what you carry.<br />
          Nothing leaves this device.
        </p>
        <button className="btn-begin" onClick={onBegin}>Begin</button>
        <p className="home-note">Local only. No accounts. No uploads.</p>
      </div>
    </div>
  )
}
