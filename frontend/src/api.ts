import axios from 'axios'

// Base URL: the Vite dev server proxies /api to the Django backend on :8000.
// In production point VITE_API_ROOT at the real API origin.
const API_ROOT = import.meta.env.VITE_API_ROOT || '/api/v1'

export const api = axios.create({ baseURL: API_ROOT })

const TOKEN_KEY = 'sms_access'
const REFRESH_KEY = 'sms_refresh'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}
export function setTokens(access: string, refresh: string) {
  localStorage.setItem(TOKEN_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
}
export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

/** Pull a human-readable message out of an API error response. */
export function errMsg(e: unknown): string {
  const err = e as { response?: { data?: { detail?: string } }; message?: string }
  return err?.response?.data?.detail || err?.message || 'Something went wrong'
}

// Attach the JWT to every request; try a refresh once when it expires.
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let refreshing: Promise<string> | null = null

async function refreshAccessToken(): Promise<string> {
  const refresh = localStorage.getItem(REFRESH_KEY)
  if (!refresh) throw new Error('no refresh token')
  const { data } = await axios.post(`${API_ROOT}/auth/token/refresh/`, {
    refresh,
  })
  localStorage.setItem(TOKEN_KEY, data.access)
  return data.access
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retried) {
      original._retried = true
      try {
        refreshing = refreshing || refreshAccessToken()
        const token = await refreshing
        refreshing = null
        original.headers.Authorization = `Bearer ${token}`
        return api(original)
      } catch {
        refreshing = null
        clearTokens()
        window.location.assign('/login')
      }
    }
    return Promise.reject(error)
  },
)

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  phone: string
  tenant: number | null
  is_verified: boolean
  is_active: boolean
  created_at: string
  permissions?: string[]
}

export type Role = 'super_admin' | 'admin' | 'teacher' | 'student' | 'parent'

export const ROLE_LABELS: Record<string, string> = {
  super_admin: 'Super Admin',
  admin: 'School Admin',
  teacher: 'Teacher',
  student: 'Student',
  parent: 'Parent',
}
