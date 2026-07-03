import test from 'node:test'
import assert from 'node:assert/strict'

import {
  clearAuthSession,
  loadAuthSession,
  saveAuthSession,
} from '../src/stores/auth-session.js'

function createStorage() {
  const values = new Map()
  return {
    getItem(key) {
      return values.has(key) ? values.get(key) : null
    },
    setItem(key, value) {
      values.set(key, String(value))
    },
    removeItem(key) {
      values.delete(key)
    },
  }
}

test('auth session round-trips through storage', () => {
  const storage = createStorage()
  saveAuthSession(storage, {
    accessToken: 'access-1',
    refreshToken: 'refresh-1',
    user: { id: 'u-1', username: 'admin' },
  })

  assert.deepEqual(loadAuthSession(storage), {
    accessToken: 'access-1',
    refreshToken: 'refresh-1',
    user: { id: 'u-1', username: 'admin' },
  })

  clearAuthSession(storage)
  assert.equal(loadAuthSession(storage), null)
})
