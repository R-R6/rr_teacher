/**
 * API request helpers.
 */

export { API_BASE } from './config.js'
import { API_BASE } from './config.js'

const BASE_URL = API_BASE + '/api'

export function buildDownloadUrl(url) {
  if (!url) return ''
  const fullUrl = url.startsWith('http') ? url : API_BASE + url
  if (fullUrl.includes('?')) return fullUrl
  return fullUrl.split('/').map((part, index) => index < 3 ? part : encodeURIComponent(part)).join('/')
}

function getToken() {
  return uni.getStorageSync('access_token') || ''
}

function request(options) {
  return new Promise((resolve, reject) => {
    const token = getToken()
    const showErrorToast = options.showErrorToast !== false
    const header = {
      'Content-Type': 'application/json',
      ...(options.header || {})
    }
    if (token) {
      header.Authorization = `Bearer ${token}`
    }

    uni.request({
      url: options.url.startsWith('http') ? options.url : `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data,
      header,
      timeout: options.timeout || 30000,
      success: (res) => {
        if (res.statusCode === 200) {
          const body = res.data
          if (body.code === 0) {
            resolve(body.data)
          } else {
            if (showErrorToast) {
              uni.showToast({ title: body.message || '请求失败', icon: 'none' })
            }
            reject(body)
          }
        } else if (res.statusCode === 401) {
          handleTokenExpired()
            .then(() => request(options).then(resolve).catch(reject))
            .catch(() => {
              uni.removeStorageSync('access_token')
              uni.removeStorageSync('refresh_token')
              uni.removeStorageSync('user_info')
              uni.reLaunch({ url: '/pages/login/login' })
              reject({ code: 401, message: '登录已过期' })
            })
        } else {
          const msg = res.data?.detail || res.data?.message || `请求错误 ${res.statusCode}`
          if (showErrorToast) {
            uni.showToast({ title: msg, icon: 'none' })
          }
          reject(res.data)
        }
      },
      fail: (err) => {
        if (showErrorToast) {
          uni.showToast({ title: '网络连接失败', icon: 'none' })
        }
        reject(err)
      }
    })
  })
}

async function handleTokenExpired() {
  const refreshToken = uni.getStorageSync('refresh_token')
  if (!refreshToken) throw new Error('No refresh token')

  const res = await new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}/auth/refresh`,
      method: 'POST',
      data: { refresh_token: refreshToken },
      header: { 'Content-Type': 'application/json' },
      success: (r) => resolve(r),
      fail: reject
    })
  })

  if (res.statusCode === 200 && res.data?.code === 0) {
    const { access_token, refresh_token } = res.data.data
    uni.setStorageSync('access_token', access_token)
    uni.setStorageSync('refresh_token', refresh_token)
    return true
  }
  throw new Error('Refresh failed')
}

function uploadImageFile(url, filePath, formData = {}) {
  return new Promise((resolve, reject) => {
    const token = getToken()
    const rejectWithToast = (body, fallback) => {
      const message = (body && (body.detail || body.message)) || fallback
      uni.showToast({ title: message, icon: 'none', duration: 2500 })
      reject({ ...(body || {}), message, _toastShown: true })
    }
    uni.uploadFile({
      url,
      filePath,
      name: 'file',
      formData,
      header: token ? { Authorization: `Bearer ${token}` } : {},
      timeout: 120000,
      success: (res) => {
        let body = {}
        try {
          body = JSON.parse(res.data || '{}')
        } catch (error) {
          body = { detail: `请求错误 ${res.statusCode || ''}`.trim() }
        }
        if (res.statusCode === 200 && body.code === 0) {
          resolve(body.data)
        } else {
          rejectWithToast(body, '上传失败')
        }
      },
      fail: (err) => {
        uni.showToast({ title: '上传失败', icon: 'none' })
        reject({ ...err, message: '上传失败', _toastShown: true })
      }
    })
  })
}

export const authAPI = {
  login: (data) => request({ url: '/auth/login', method: 'POST', data }),
  register: (data) => request({ url: '/auth/register', method: 'POST', data }),
  wechatLogin: (data) => request({ url: '/auth/wechat-login', method: 'POST', data }),
  getMe: () => request({ url: '/auth/me' }),
  updateMe: (data) => request({ url: '/auth/me', method: 'PUT', data }),
  bindPhone: (phone) => request({ url: `/auth/bind-phone?phone=${phone}`, method: 'POST' }),
}

export const questionsAPI = {
  list: (params) => request({ url: '/questions/', data: params }),
  detail: (id) => request({ url: `/questions/${id}` }),
  create: (data) => request({ url: '/questions/', method: 'POST', data }),
  update: (id, data) => request({ url: `/questions/${id}`, method: 'PUT', data }),
  delete: (id) => request({ url: `/questions/${id}`, method: 'DELETE' }),
  batchDelete: (ids) => request({ url: '/questions/batch-delete', method: 'POST', data: { ids } }),
}

export const ocrAPI = {
  recognize: (filePath, engine = 'tesseract') =>
    uploadImageFile(`${BASE_URL}/ocr/recognize`, filePath, { engine }),
  listEngines: () => request({ url: '/ocr/engines' }),
  correct: (data) => request({ url: '/ocr/correct', method: 'POST', data }),
  history: (params) => request({ url: '/ocr/history', data: params }),
}

export const uploadAPI = {
  image: (filePath, purpose = 'manual_input') =>
    uploadImageFile(`${BASE_URL}/upload/image`, filePath, { purpose }),
}

export const papersAPI = {
  list: (params) => request({ url: '/papers/', data: params }),
  detail: (id) => request({ url: `/papers/${id}` }),
  createManual: (data) => request({ url: '/papers/manual', method: 'POST', data }),
  createAuto: (data) => request({ url: '/papers/auto', method: 'POST', data }),
  delete: (id) => request({ url: `/papers/${id}`, method: 'DELETE' }),
}

export const tagsAPI = {
  list: (params) => request({ url: '/tags/', data: params }),
  create: (data) => request({ url: '/tags/', method: 'POST', data }),
  delete: (id) => request({ url: `/tags/${id}`, method: 'DELETE' }),
  seed: () => request({ url: '/tags/seed', method: 'POST' }),
}

export const practiceAPI = {
  getQuestions: (params) => request({ url: '/practice/questions', data: params }),
  submitAnswer: (data) => request({ url: '/practice/submit', method: 'POST', data }),
  getStats: () => request({ url: '/practice/stats' }),
  getTrend: (days) => request({ url: `/practice/trend?days=${days || 7}` }),
}

export const mistakesAPI = {
  list: (params) => request({ url: '/mistakes', data: params }),
  add: (questionId) => request({ url: '/mistakes', method: 'POST', data: { question_id: questionId } }),
  markMastered: (id) => request({ url: `/mistakes/${id}/master`, method: 'PUT' }),
  delete: (id) => request({ url: `/mistakes/${id}`, method: 'DELETE' }),
  updateNotes: (id, notes) => request({ url: `/mistakes/${id}/notes`, method: 'PUT', data: { notes } }),
  getStats: () => request({ url: '/mistakes/stats' }),
}

export const exportAPI = {
  paperWord: (paperId, includeAnswer) => {
    const suffix = includeAnswer === false ? '?include_answer=false' : ''
    return request({ url: `/export/paper/${paperId}/word${suffix}`, method: 'POST', showErrorToast: false })
  },
  questionsWord: (data) => request({ url: '/export/questions/word', method: 'POST', data }),
}

export default {
  auth: authAPI,
  questions: questionsAPI,
  ocr: ocrAPI,
  upload: uploadAPI,
  papers: papersAPI,
  tags: tagsAPI,
  export: exportAPI,
}
