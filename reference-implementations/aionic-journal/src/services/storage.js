import Dexie from 'dexie'

/**
 * storage.js — IndexedDB persistence via Dexie.
 * Replaces localStorage. Async API, 50MB+ cap, survives browser data cleans.
 * Schema: entries keyed by id, indexed on created_at for sort.
 */

const db = new Dexie('AionicJournal')
db.version(1).stores({
  entries: 'id, created_at',
})

function newId() {
  return `entry:${Date.now()}:${Math.random().toString(36).substr(2, 9)}`
}

export async function storeEntry(entry) {
  const newEntry = {
    ...entry,
    id: entry.id || newId(),
    created_at: entry.created_at || new Date().toISOString(),
    updated_at: new Date().toISOString(),
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
