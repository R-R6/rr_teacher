/**
 * API 请求封装
 * 统一处理请求、响应、错误、Token 刷新
 */

// 后端地址（不含 /api 后缀）
// 开发环境: http://10.168.3.24:8000（本机后端）
// 生产环境: 云托管域名
export const API_BASE = 'https://chem-backend-268016-4-1440725000.sh.run.tcloudbase.com'
const BASE_URL = API_BASE + '/api'

// 请求拦截器 - 自动附加 Token
function getToken() {
  return uni.getStorageSync('access_token') || ''
}

// 统一请求方法
function request(options) {
  return new Promise((resolve, reject) => {
    const token = getToken()
    const header = {
      'Content-Type': 'application/json',
      ...(options.header || {})
    }
    if (token) {
      header['Authorization'] = `Bearer ${token}`
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
            uni.showToast({ title: body.message || '请求失败', icon: 'none' })
            reject(body)
          }
        } else if (res.statusCode === 401) {
          // Token 过期，尝试刷新
          handleTokenExpired().then(() => {
            // 重试原请求
            request(options).then(resolve).catch(reject)
          }).catch(() => {
            uni.removeStorageSync('access_token')
            uni.removeStorageSync('refresh_token')
            uni.removeStorageSync('user_info')
            uni.reLaunch({ url: '/pages/login/login' })
            reject({ code: 401, message: '登录已过期' })
          })
        } else {
          const msg = res.data?.detail || res.data?.message || `请求错误 ${res.statusCode}`
          uni.showToast({ title: msg, icon: 'none' })
          reject(res.data)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络连接失败', icon: 'none' })
        reject(err)
      }
    })
  })
}

// Token 刷新
async function handleTokenExpired() {
  const refreshToken = uni.getStorageSync('refresh_token')
  if (!refreshToken) throw new Error('无 refresh_token')

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
  throw new Error('刷新失败')
}

// ========== Auth API ==========
export const authAPI = {
  login: (data) => request({ url: '/auth/login', method: 'POST', data }),
  register: (data) => request({ url: '/auth/register', method: 'POST', data }),
  wechatLogin: (data) => request({ url: '/auth/wechat-login', method: 'POST', data }),
  getMe: () => request({ url: '/auth/me' }),
  bindPhone: (phone) => request({ url: `/auth/bind-phone?phone=${phone}`, method: 'POST' }),
}

// ========== Questions API ==========
export const questionsAPI = {
  list: (params) => request({ url: '/questions/', data: params }),
  detail: (id) => request({ url: `/questions/${id}` }),
  create: (data) => request({ url: '/questions/', method: 'POST', data }),
  update: (id, data) => request({ url: `/questions/${id}`, method: 'PUT', data }),
  delete: (id) => request({ url: `/questions/${id}`, method: 'DELETE' }),
  batchDelete: (ids) => request({ url: '/questions/batch-delete', method: 'POST', data: { ids } }),
}

// ========== OCR API ==========
export const ocrAPI = {
  recognize: (filePath) => {
    return new Promise((resolve, reject) => {
      const token = getToken()
      uni.uploadFile({
        url: `${BASE_URL}/ocr/recognize`,
        filePath,
        name: 'file',
        header: { Authorization: `Bearer ${token}` },
        success: (res) => {
          const body = JSON.parse(res.data)
          if (body.code === 0) {
            resolve(body.data)
          } else {
            uni.showToast({ title: body.message || '识别失败', icon: 'none' })
            reject(body)
          }
        },
        fail: (err) => {
          uni.showToast({ title: '上传失败', icon: 'none' })
          reject(err)
        }
      })
    })
  },
  correct: (data) => request({ url: '/ocr/correct', method: 'POST', data }),
  history: (params) => request({ url: '/ocr/history', data: params }),
}

// ========== Papers API ==========
export const papersAPI = {
  list: (params) => request({ url: '/papers/', data: params }),
  detail: (id) => request({ url: `/papers/${id}` }),
  createManual: (data) => request({ url: '/papers/manual', method: 'POST', data }),
  createAuto: (data) => request({ url: '/papers/auto', method: 'POST', data }),
  delete: (id) => request({ url: `/papers/${id}`, method: 'DELETE' }),
}

// ========== Tags API ==========
export const tagsAPI = {
  list: (params) => request({ url: '/tags/', data: params }),
  create: (data) => request({ url: '/tags/', method: 'POST', data }),
  delete: (id) => request({ url: `/tags/${id}`, method: 'DELETE' }),
  seed: () => request({ url: '/tags/seed', method: 'POST' }),
}

// ========== Export API ==========
export const exportAPI = {
  paperWord: (paperId, includeAnswer) => {
    const suffix = includeAnswer === false ? '?include_answer=false' : ''
    return request({ url: `/export/paper/${paperId}/word${suffix}`, method: 'POST' })
  },
  questionsWord: (data) => request({ url: '/export/questions/word', method: 'POST', data }),
}

export default {
  auth: authAPI,
  questions: questionsAPI,
  ocr: ocrAPI,
  papers: papersAPI,
  tags: tagsAPI,
  export: exportAPI,
}
