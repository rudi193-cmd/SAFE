import { useState } from 'react'
import { Layout } from './ui/Layout'
import { Page1Home } from './pages/Page1Home'
import { Page2Consent } from './pages/Page2Consent'
import { Page3Journal } from './pages/Page3Journal'

/**
 * App — page orchestrator.
 * 1 → Home, 2 → Consent, 3 → Journal
 */
export default function App() {
  const [page, setPage] = useState(1)
  const [consented, setConsented] = useState(false)

  if (page === 1) {
    return (
      <Layout>
        <Page1Home onBegin={() => setPage(2)} />
      </Layout>
    )
  }

  if (page === 2) {
    return (
      <Layout>
        <Page2Consent
          onConsent={() => { setConsented(true); setPage(3) }}
          onDecline={() => { setConsented(false); setPage(3) }}
        />
      </Layout>
    )
  }

  return (
    <Layout>
      <Page3Journal consented={consented} />
    </Layout>
  )
}
