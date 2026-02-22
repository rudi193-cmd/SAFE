/**
 * session.js -- capture session identity and timing.
 */
function shortId() {
  return Math.random().toString(36).substr(2, 6)
}

export function generateSessionId() {
  const date = new Date().toISOString().split('T')[0]
  return 'jane-' + date + '-' + shortId()
}

export function sessionTimer() {
  const startMs = Date.now()
  return {
    elapsed: () => Math.round((Date.now() - startMs) / 1000),
  }
}
