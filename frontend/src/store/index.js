/**
 * 简单状态管理
 */
import { reactive } from 'vue'
import { getUserInfo, isLoggedIn } from '../utils/auth.js'

const state = reactive({
  user: getUserInfo(),
  loggedIn: isLoggedIn(),
})

export function createStore() {
  return {
    state,
    login(userInfo, tokens) {
      state.user = userInfo
      state.loggedIn = true
      uni.setStorageSync('user_info', JSON.stringify(userInfo))
      uni.setStorageSync('access_token', tokens.access_token)
      uni.setStorageSync('refresh_token', tokens.refresh_token)
    },
    logout() {
      state.user = null
      state.loggedIn = false
      uni.removeStorageSync('user_info')
      uni.removeStorageSync('access_token')
      uni.removeStorageSync('refresh_token')
      uni.reLaunch({ url: '/pages/login/login' })
    },
    updateUser(info) {
      state.user = { ...state.user, ...info }
      uni.setStorageSync('user_info', JSON.stringify(state.user))
    },
  }
}
