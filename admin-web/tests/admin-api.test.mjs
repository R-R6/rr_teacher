import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const rootDir = path.dirname(fileURLToPath(import.meta.url))
const adminApiSource = readFileSync(path.join(rootDir, '../src/api/admin.js'), 'utf-8')

test('adminApi exposes getAdminMe for login handoff', () => {
  assert.match(adminApiSource, /export const authApi = \{[\s\S]*getAdminMe\(\)/)
  assert.match(adminApiSource, /export const adminApi = \{[\s\S]*getAdminMe\(\)/)
})

test('adminApi exposes billing seed offer operations', () => {
  assert.match(adminApiSource, /getBillingSeedSummary\(\)/)
  assert.match(adminApiSource, /listBillingEligibilities\(params\)/)
  assert.match(adminApiSource, /listBillingOrders\(params\)/)
  assert.match(adminApiSource, /listBillingEntitlements\(params\)/)
  assert.match(adminApiSource, /closeBillingOrder\(orderId\)/)
  assert.match(adminApiSource, /releaseBillingEligibility\(eligibilityId\)/)
  assert.match(adminApiSource, /grantBillingEntitlement\(payload\)/)

  assert.match(adminApiSource, /\/admin\/billing\/seed-summary/)
  assert.match(adminApiSource, /\/admin\/billing\/eligibilities/)
  assert.match(adminApiSource, /\/admin\/billing\/orders/)
  assert.match(adminApiSource, /\/admin\/billing\/entitlements/)
  assert.match(adminApiSource, /\/close/)
  assert.match(adminApiSource, /\/release/)
  assert.match(adminApiSource, /\/entitlements\/grant/)
})
