import { computed, reactive } from 'vue'

import { clearAuthSession, loadAuthSession, saveAuthSession } from './auth-session.js'

const state = reactive({
  accessToken: '',
  refreshToken: '',
  user: null,
  hydrated: false,
})

export function hydrateAuthState() {
  if (state.hydrated) return
  const session = loadAuthSession()
  if (session) {
    state.accessToken = session.accessToken
    state.refreshToken = session.refreshToken
    state.user = session.user
  }
  state.hydrated = true
}

export function setAuthSession(session) {
  state.accessToken = session.accessToken
  state.refreshToken = session.refreshToken
  state.user = session.user
  saveAuthSession(window.localStorage, session)
}

export function clearAuthState() {
  state.accessToken = ''
  state.refreshToken = ''
  state.user = null
  clearAuthSession(window.localStorage)
}

export function useAuthStore() {
  return {
    state,
    isAuthenticated: computed(() => !!state.accessToken && !!state.user),
  }
}
