const ACCESS_KEY = 'chem_admin_access_token'
const REFRESH_KEY = 'chem_admin_refresh_token'
const USER_KEY = 'chem_admin_user'

export function loadAuthSession(storage = window.localStorage) {
  const accessToken = storage.getItem(ACCESS_KEY)
  const refreshToken = storage.getItem(REFRESH_KEY)
  const userRaw = storage.getItem(USER_KEY)

  if (!accessToken || !refreshToken || !userRaw) {
    return null
  }

  try {
    return {
      accessToken,
      refreshToken,
      user: JSON.parse(userRaw),
    }
  } catch {
    clearAuthSession(storage)
    return null
  }
}

export function saveAuthSession(storage = window.localStorage, session) {
  storage.setItem(ACCESS_KEY, session.accessToken)
  storage.setItem(REFRESH_KEY, session.refreshToken)
  storage.setItem(USER_KEY, JSON.stringify(session.user))
}

export function clearAuthSession(storage = window.localStorage) {
  storage.removeItem(ACCESS_KEY)
  storage.removeItem(REFRESH_KEY)
  storage.removeItem(USER_KEY)
}
