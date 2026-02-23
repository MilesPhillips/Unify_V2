import { useAuth } from '../contexts/AuthContext'

export default function Profile() {
  const { user } = useAuth()

  return (
    <div className="page">
      <h1 style={{ marginBottom: '1.5rem' }}>Profile</h1>
      <div className="card" style={{ maxWidth: 480 }}>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
          Username
        </p>
        <p style={{ fontSize: '1.1rem', fontWeight: 600 }}>{user?.username}</p>
      </div>
      <p style={{ marginTop: '2rem', color: 'var(--color-text-muted)' }}>
        More profile settings coming soon.
      </p>
    </div>
  )
}
