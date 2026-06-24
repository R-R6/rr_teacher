export const DEFAULT_API_BASE = 'https://chem-backend-268016-4-1440725000.sh.run.tcloudbase.com'

export function normalizeApiBase(value) {
  const base = String(value || '').trim()
  if (!base) return DEFAULT_API_BASE
  return base.replace(/\/+$/, '')
}

export function resolveApiBase(env = import.meta.env) {
  const values = env || {}
  return normalizeApiBase(values.VITE_API_BASE || values.UNI_API_BASE || DEFAULT_API_BASE)
}

export const API_BASE = resolveApiBase()
