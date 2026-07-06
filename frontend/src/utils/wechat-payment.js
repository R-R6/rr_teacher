function resolveRequestPayment(requestPayment) {
  if (typeof requestPayment === 'function') {
    return requestPayment
  }

  if (typeof uni !== 'undefined' && typeof uni.requestPayment === 'function') {
    return (paymentParams) =>
      new Promise((resolve, reject) => {
        uni.requestPayment({
          ...paymentParams,
          success: resolve,
          fail: reject,
        })
      })
  }

  throw new Error('微信支付能力不可用')
}

export function validatePaymentParams(paymentParams) {
  const requiredFields = ['timeStamp', 'nonceStr', 'package', 'signType', 'paySign']
  const missingField = requiredFields.find((field) => !paymentParams?.[field])

  if (missingField) {
    throw new Error(`缺少支付参数：${missingField}`)
  }
}

export function isPaymentConfirmed(order, entitlement) {
  const orderStatus = String(order?.status || '').toLowerCase()
  return orderStatus === 'paid' || entitlement?.active === true || entitlement?.status === 'active'
}

export async function payWithWechatAndConfirm(options) {
  const {
    orderId,
    paymentParams,
    requestPayment,
    confirmOrder,
  } = options || {}

  if (!orderId) {
    throw new Error('缺少订单编号')
  }
  if (typeof confirmOrder !== 'function') {
    throw new Error('缺少订单确认方法')
  }

  validatePaymentParams(paymentParams)

  const runRequestPayment = resolveRequestPayment(requestPayment)
  await runRequestPayment(paymentParams)

  return confirmOrder(orderId)
}
