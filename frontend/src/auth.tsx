import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { api, clearTokens, getToken, setTokens, User } from './api'

interface AuthState {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState>({
  user: null,
  loading: true,
  login: async () => {},
  logout: () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      if (!getToken()) {
        setLoading(false)
        return
      }
      try {
        const { data } = await api.get<User>('/me/')
        setUser(data)
      } catch {
        clearTokens()
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  async function login(username: string, password: string) {
    const { data } = await api.post('/auth/token/', { username, password })
    setTokens(data.access, data.refresh)
    const me = await api.get<User>('/me/')
    setUser(me.data)
  }

  function logout() {
    clearTokens()
    setUser(null)
    window.location.assign('/login')
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
