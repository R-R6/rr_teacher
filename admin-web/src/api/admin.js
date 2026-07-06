import { apiClient } from './client.js'

function withParams(path, params = {}) {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue
    search.set(key, value)
  }
  const suffix = search.toString()
  return suffix ? `${path}?${suffix}` : path
}

export const authApi = {
  login(payload) {
    return apiClient.publicPost('/auth/login', payload)
  },
  getAdminMe() {
    return apiClient.get('/admin/me')
  },
}

export const adminApi = {
  getAdminMe() {
    return apiClient.get('/admin/me')
  },
  getDashboardSummary() {
    return apiClient.get('/admin/dashboard/summary')
  },
  getDashboardTrend(days = 7) {
    return apiClient.get(withParams('/admin/dashboard/ocr-trend', { days }))
  },
  getRecentRisks() {
    return apiClient.get('/admin/dashboard/recent-risks')
  },
  listQuestions(params) {
    return apiClient.get(withParams('/admin/questions', params))
  },
  getQuestionDetail(id) {
    return apiClient.get(`/admin/questions/${id}`)
  },
  updateQuestion(id, payload) {
    return apiClient.put(`/admin/questions/${id}`, payload)
  },
  deleteQuestion(id) {
    return apiClient.delete(`/admin/questions/${id}`)
  },
  listTags(params) {
    return apiClient.get(withParams('/admin/tags', params))
  },
  createTag(payload) {
    return apiClient.post('/admin/tags', payload)
  },
  updateTag(id, payload) {
    return apiClient.put(`/admin/tags/${id}`, payload)
  },
  deleteTag(id) {
    return apiClient.delete(`/admin/tags/${id}`)
  },
  listOcrRecords(params) {
    return apiClient.get(withParams('/admin/ocr-records', params))
  },
  getOcrRecord(id) {
    return apiClient.get(`/admin/ocr-records/${id}`)
  },
  correctOcrRecord(id, payload) {
    return apiClient.post(`/admin/ocr-records/${id}/correct`, payload)
  },
  listPapers(params) {
    return apiClient.get(withParams('/admin/papers', params))
  },
  deletePaper(id) {
    return apiClient.delete(`/admin/papers/${id}`)
  },
  listUsers(params) {
    return apiClient.get(withParams('/admin/users', params))
  },
  getUserDetail(id) {
    return apiClient.get(`/admin/users/${id}`)
  },
  getUserOcrUsage(id, params) {
    return apiClient.get(withParams(`/admin/users/${id}/ocr-usage`, params))
  },
  updateUserQuotaProfile(id, payload) {
    return apiClient.put(`/admin/users/${id}/quota-profile`, payload)
  },
  getOcrUsage(days = 7) {
    return apiClient.get(withParams('/admin/cost/ocr-usage', { days }))
  },
  getBillingSeedSummary() {
    return apiClient.get('/admin/billing/seed-summary')
  },
  listBillingEligibilities(params) {
    return apiClient.get(withParams('/admin/billing/eligibilities', params))
  },
  listBillingOrders(params) {
    return apiClient.get(withParams('/admin/billing/orders', params))
  },
  listBillingEntitlements(params) {
    return apiClient.get(withParams('/admin/billing/entitlements', params))
  },
  closeBillingOrder(orderId) {
    return apiClient.post(`/admin/billing/orders/${orderId}/close`, {})
  },
  releaseBillingEligibility(eligibilityId) {
    return apiClient.post(`/admin/billing/eligibilities/${eligibilityId}/release`, {})
  },
  grantBillingEntitlement(payload) {
    return apiClient.post('/admin/billing/entitlements/grant', payload)
  },
  getSystemStatus() {
    return apiClient.get('/admin/system/status')
  },
}
