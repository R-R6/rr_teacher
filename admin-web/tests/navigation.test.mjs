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
    'billing',
    'system-status',
  ])

  const billingItem = NAV_ITEMS.find((item) => item.key === 'billing')
  assert.equal(billingItem.path, '/billing')
  assert.equal(billingItem.label, '计费权益')
})
