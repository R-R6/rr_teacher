import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import test from 'node:test'

const apiSource = readFileSync(new URL('../src/utils/api.js', import.meta.url), 'utf8')
const profileSource = readFileSync(new URL('../src/pages/profile/profile.vue', import.meta.url), 'utf8')
const pagesJson = JSON.parse(readFileSync(new URL('../src/pages.json', import.meta.url), 'utf8'))
const seedOfferPageUrl = new URL('../src/pages/billing/seed-offer.vue', import.meta.url)
const paymentAdapterUrl = new URL('../src/utils/wechat-payment.js', import.meta.url)

test('profile page links seed pricing from the My tab without adding a bottom tab', () => {
  assert.match(profileSource, /\/pages\/billing\/seed-offer/)
  assert.match(profileSource, /种子计划|终身权益/)

  assert.ok(pagesJson.pages.some((page) => page.path === 'pages/billing/seed-offer'))
  assert.equal(
    pagesJson.tabBar.list.some((item) => item.pagePath === 'pages/billing/seed-offer'),
    false,
  )
})

test('billing API exposes seed offer, claim, order create, and order status helpers', () => {
  assert.match(apiSource, /export const billingAPI/)
  assert.match(apiSource, /\/billing\/seed-offer/)
  assert.match(apiSource, /\/billing\/seed-offer\/claim/)
  assert.match(apiSource, /\/billing\/orders/)
  assert.match(apiSource, /\/billing\/orders\/\$\{orderId\}/)
  assert.match(apiSource, /\/billing\/me\/entitlements/)
})

test('wechat payment adapter requires payment params and confirms order after requestPayment', async () => {
  assert.equal(existsSync(paymentAdapterUrl), true)

  const { isPaymentConfirmed, payWithWechatAndConfirm } = await import(paymentAdapterUrl.href)
  const calls = []
  const requester = (params) => {
    calls.push(['requestPayment', params])
    return Promise.resolve({ errMsg: 'requestPayment:ok' })
  }
  const confirmOrder = (orderId) => {
    calls.push(['confirmOrder', orderId])
    return Promise.resolve({ id: orderId, status: 'paid' })
  }

  const result = await payWithWechatAndConfirm({
    orderId: 7,
    paymentParams: { timeStamp: '1', nonceStr: 'n', package: 'prepay_id=x', signType: 'RSA', paySign: 's' },
    requestPayment: requester,
    confirmOrder,
  })

  assert.deepEqual(calls, [
    ['requestPayment', { timeStamp: '1', nonceStr: 'n', package: 'prepay_id=x', signType: 'RSA', paySign: 's' }],
    ['confirmOrder', 7],
  ])
  assert.equal(result.status, 'paid')
  assert.equal(isPaymentConfirmed({ status: 'paid' }), true)
  assert.equal(isPaymentConfirmed({ status: 'pending' }), false)
  assert.equal(isPaymentConfirmed({ status: 'created' }, { active: true }), true)
  assert.equal(isPaymentConfirmed({ status: 'created' }, { status: 'active' }), true)
})

test('seed offer page keeps frontend payment success separate from final entitlement state', () => {
  assert.equal(existsSync(seedOfferPageUrl), true)

  const source = readFileSync(seedOfferPageUrl, 'utf8')
  assert.match(source, /payWithWechatAndConfirm/)
  assert.match(source, /isPaymentConfirmed\(confirmed, this\.entitlement\)/)
  assert.match(source, /支付结果等待确认/)
  assert.match(source, /loadSeedOffer/)
  assert.match(source, /支付完成，正在确认权益/)
  assert.doesNotMatch(source, /支付成功.*已开通/)
})
