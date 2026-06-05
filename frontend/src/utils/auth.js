/**
 * 认证工具函数
 */

export function isLoggedIn() {
  return !!uni.getStorageSync('access_token')
}

export function getUserInfo() {
  try {
    const raw = uni.getStorageSync('user_info')
    return raw ? (typeof raw === 'string' ? JSON.parse(raw) : raw) : null
  } catch {
    return null
  }
}

export function setUserInfo(info) {
  uni.setStorageSync('user_info', JSON.stringify(info))
}

export function setTokens(accessToken, refreshToken) {
  uni.setStorageSync('access_token', accessToken)
  uni.setStorageSync('refresh_token', refreshToken)
}

export function clearAuth() {
  uni.removeStorageSync('access_token')
  uni.removeStorageSync('refresh_token')
  uni.removeStorageSync('user_info')
}

export function checkLogin() {
  if (!isLoggedIn()) {
    uni.reLaunch({ url: '/pages/login/login' })
    return false
  }
  return true
}

export function isTeacher() {
  const user = getUserInfo()
  return user?.role === 'teacher'
}
