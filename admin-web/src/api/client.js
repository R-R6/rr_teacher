import { clearAuthState, setAuthSession, useAuthStore } from '@/stores/auth.js'

const API_BASE = (import.meta.env.VITE_ADMIN_API_BASE || '').replace(/\/$/, '')
const { state } = useAuthStore()

let refreshPromise = null

function buildUrl(path) {
  return `${API_BASE}/api${path}`
}

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    return null
  }
  return response.json()
}

async function refreshAccessToken() {
  if (refreshPromise) return refreshPromise
  if (!state.refreshToken) {
    throw new Error('缺少刷新令牌')
  }

  refreshPromise = fetch(buildUrl('/auth/refresh'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: state.refreshToken }),
  })
    .then(async (response) => {
      const body = await parseResponse(response)
      if (!response.ok || !body || body.code !== 0) {
        throw new Error(body?.detail || body?.message || '刷新登录失败')
      }
      setAuthSession({
        accessToken: body.data.access_token,
        refreshToken: state.refreshToken,
        user: state.user,
      })
      return body.data.access_token
    })
    .finally(() => {
      refreshPromise = null
    })

  return refreshPromise
}

async function request(path, options = {}, retrying = false) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }
  if (options.auth !== false && state.accessToken) {
    headers.Authorization = `Bearer ${state.accessToken}`
  }

  const response = await fetch(buildUrl(path), {
    method: options.method || 'GET',
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  if (response.status === 401 && options.auth !== false && !retrying && state.refreshToken) {
    try {
      await refreshAccessToken()
      return request(path, options, true)
    } catch (error) {
      clearAuthState()
      throw error
    }
  }

  const body = await parseResponse(response)
  if (!response.ok) {
    throw new Error(body?.detail || body?.message || `请求失败 ${response.status}`)
  }
  if (!body || body.code !== 0) {
    throw new Error(body?.message || '接口返回异常')
  }
  return body.data
}

export const apiClient = {
  get(path) {
    return request(path)
  },
  post(path, body, options = {}) {
    return request(path, { ...options, method: 'POST', body })
  },
  put(path, body, options = {}) {
    return request(path, { ...options, method: 'PUT', body })
  },
  delete(path, body, options = {}) {
    return request(path, { ...options, method: 'DELETE', body })
  },
  publicPost(path, body) {
    return request(path, { method: 'POST', body, auth: false })
  },
}
