import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const rootDir = path.dirname(fileURLToPath(import.meta.url))
const billingPageSource = readFileSync(path.join(rootDir, '../src/pages/BillingPage.vue'), 'utf-8')
const routerSource = readFileSync(path.join(rootDir, '../src/router/index.js'), 'utf-8')

test('BillingPage is registered as an admin route', () => {
  assert.match(routerSource, /BillingPage/)
  assert.match(routerSource, /path: 'billing'/)
  assert.match(routerSource, /计费权益/)
})

test('BillingPage shows seed summary, eligibility, order, and entitlement ledgers', () => {
  assert.match(billingPageSource, /种子计划摘要/)
  assert.match(billingPageSource, /资格/)
  assert.match(billingPageSource, /订单/)
  assert.match(billingPageSource, /权益/)
  assert.match(billingPageSource, /MetricCard/)
  assert.match(billingPageSource, /PanelCard/)
  assert.match(billingPageSource, /StatusPill/)
  assert.match(billingPageSource, /ListStateSummary/)
})

test('BillingPage covers billing fields and admin actions', () => {
  assert.match(billingPageSource, /free_used/)
  assert.match(billingPageSource, /paid_locked/)
  assert.match(billingPageSource, /paid_paid/)
  assert.match(billingPageSource, /amount_cents/)
  assert.match(billingPageSource, /slot_no/)
  assert.match(billingPageSource, /order_no/)
  assert.match(billingPageSource, /transaction_id/)
  assert.match(billingPageSource, /source/)

  assert.match(billingPageSource, /closeBillingOrder/)
  assert.match(billingPageSource, /releaseBillingEligibility/)
  assert.match(billingPageSource, /grantBillingEntitlement/)
})
