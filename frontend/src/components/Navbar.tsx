import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const NAV_LINKS = [
  { to: '/chat', label: 'Chat' },
  { to: '/ai-coach', label: 'AI Coach' },
  { to: '/contacts', label: 'Contacts' },
  { to: '/history', label: 'History' },
  { to: '/video', label: 'Video' },
]

export default function Navbar() {
  const { user, logout } = useAuth()
  const location = useLocation()

  // Don't render the navbar on auth pages
  if (!user) return null

  return (
    <nav
      style={{
        height: 60,
        display: 'flex',
        alignItems: 'center',
        padding: '0 1.5rem',
        backgroundColor: 'var(--color-surface)',
        borderBottom: '1px solid var(--color-border)',
        gap: '1.5rem',
      }}
    >
      {/* Brand */}
      <Link
        to="/chat"
        style={{
          fontWeight: 700,
          fontSize: '1.1rem',
          color: 'var(--color-accent)',
          textDecoration: 'none',
          marginRight: '0.5rem',
        }}
      >
        Unify
      </Link>

      {/* Nav links */}
      <div style={{ display: 'flex', gap: '1rem', flex: 1 }}>
        {NAV_LINKS.map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            style={{
              fontSize: '0.9rem',
              color: location.pathname === to ? 'var(--color-accent)' : 'var(--color-text-muted)',
              textDecoration: 'none',
              fontWeight: location.pathname === to ? 600 : 400,
            }}
          >
            {label}
          </Link>
        ))}
      </div>

      {/* User + logout */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <Link
          to="/profile"
          style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', textDecoration: 'none' }}
        >
          {user.username}
        </Link>
        <button className="btn btn-ghost" style={{ fontSize: '0.85rem', padding: '0.3rem 0.9rem' }} onClick={logout}>
          Sign out
        </button>
      </div>
    </nav>
  )
}
