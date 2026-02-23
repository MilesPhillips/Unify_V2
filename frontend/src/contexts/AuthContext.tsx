import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { api, isApiError } from '../lib/api'

// ─── Types ────────────────────────────────────────────────────────────────────

export interface User {
  user_id: number
  username: string
}

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

// ─── Context ──────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null)

// ─── Provider ─────────────────────────────────────────────────────────────────

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // On mount, restore session from the Flask session cookie.
  useEffect(() => {
    api.get<User>('/api/me')
      .then(setUser)
      .catch((err) => {
        // 401 just means not logged in — not an error worth logging.
        if (isApiError(err) && err.status === 401) return
        console.error('Failed to restore session:', err)
      })
      .finally(() => setIsLoading(false))
  }, [])

  async function login(username: string, password: string) {
    const data = await api.post<User>('/api/login', { username, password })
    setUser(data)
  }

  async function logout() {
    await api.post('/api/logout', {})
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
