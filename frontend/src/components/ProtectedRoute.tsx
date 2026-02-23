import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import type { ReactNode } from 'react'

interface Props {
  children: ReactNode
}

/**
 * Wraps a route so only authenticated users can access it.
 * While the session is being restored (isLoading), renders nothing.
 * Once resolved, redirects unauthenticated users to /login.
 */
export function ProtectedRoute({ children }: Props) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    // Avoid a flash-redirect while we check the session cookie.
    return null
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
