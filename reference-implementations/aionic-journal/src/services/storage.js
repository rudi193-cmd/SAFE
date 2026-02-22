import Dexie from 'dexie'

/**
 * storage.js -- IndexedDB persistence via Dexie v2.
 * Entry schema aligned with oral_stories governance pattern.
 * New fields: source_type, confidence, corrections, sources,
 *             summary, embedding_ready, capture_session, session_meta.
 * Draft helpers: localStorage, raw text only.
 */

const db = new Dexie('AionicJournal')

db.version(1).stores({
  entries: 'id, created_at',
})
db.version(2).stores({
  entries: 'id, created_at, capture_session',
})

const DRAFT_KEY = 'aionic:draft'

export async function storeEntry(entry) {
  const content = entry.content ?? entry.body ?? ''
  const newEntry = {
    id:              entry.id || crypto.randomUUID(),
    created_at:      entry.created_at || new Date().toISOString(),
    updated_at:      new Date().toISOString(),
    title:           entry.title ?? '',
    content,
    source_type:     'oral_history_consented',
    confidence:      entry.confidence ?? 'medium',
    corrections:     entry.corrections ?? [],
    sources:         entry.sources ?? [],
    summary:         entry.summary ?? '',
    embedding_ready: false,
    capture_session: entry.capture_session ?? '',
    tone:            entry.tone ?? 'reflective',
    deltaE:          entry.deltaE ?? 0,
    deleted:         false,
    deleted_at:      null,
    session_meta:    entry.session_meta ?? null,
  }
  await db.entries.put(newEntry)
  return newEntry
}

export async function getAllEntries() {
  const all = await db.entries.orderBy('created_at').reverse().toArray()
  return all.filter(e => !e.deleted)
}

export async function deleteEntry(id) {
  await db.entries.update(id, {
    deleted: true,
    deleted_at: new Date().toISOString(),
  })
}

export async function clearAll() {
  await db.entries.clear()
}

export function saveDraft(text) {
  try { localStorage.setItem(DRAFT_KEY, text) } catch (_) {}
}

export function getDraft() {
  try { return localStorage.getItem(DRAFT_KEY) || '' } catch (_) { return '' }
}

export function clearDraft() {
  try { localStorage.removeItem(DRAFT_KEY) } catch (_) {}
}
