/**
 * storage.js — Local persistence for Aionic Journal
 * Wraps localStorage with the same API as continuity/rings.js.
 * Entries survive page refresh. Nothing leaves the device.
 *
 * Key: 'aionic:entries' → JSON array, newest first
 */

const KEY = 'aionic:entries'

function load() {
  try {
    const raw = localStorage.getItem(KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function save(entries) {
  try {
    localStorage.setItem(KEY, JSON.stringify(entries))
  } catch {
    // Storage full or disabled — silently degrade to in-session only
  }
}

export function storeEntry(entry) {
  const entries = load()
  const newEntry = {
    ...entry,
    id: entry.id || `entry:${Date.now()}:${Math.random().toString(36).substr(2, 9)}`,
    created_at: entry.created_at || new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
  save([newEntry, ...entries])
  return newEntry
}

export function getAllEntries() {
  return load()
    .filter(e => !e.deleted)
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
}

export function deleteEntry(id) {
  const entries = load()
  const updated = entries.map(e =>
    e.id === id
      ? { ...e, deleted: true, deleted_at: new Date().toISOString() }
      : e
  )
  save(updated)
}

export function clearAll() {
  localStorage.removeItem(KEY)
}
