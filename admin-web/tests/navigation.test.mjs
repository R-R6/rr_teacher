import test from 'node:test'
import assert from 'node:assert/strict'

import { NAV_ITEMS, DEFAULT_ROUTE } from '../src/config/navigation.js'

test('admin navigation covers first phase modules', () => {
  const keys = NAV_ITEMS.map((item) => item.key)

  assert.equal(DEFAULT_ROUTE, '/dashboard')
  assert.deepEqual(keys, [
    'dashboard',
    'questions',
    'tags',
    'ocr-records',
    'papers',
    'users',
    'cost-monitor',
    'system-status',
  ])
})
