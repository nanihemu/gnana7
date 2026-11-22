import { Link } from 'react-router-dom'
import { useFetch } from '../../hooks'

interface Child {
  id: number
  full_name: string
  username: string
}

export default function ParentHome() {
  const { data, loading, error } = useFetch<Child[]>('/me/children/')

  return (
    <div>
      <h1>My Children</h1>
      {error && <div className="alert error">{error}</div>}
      {loading && <p className="muted">Loading…</p>}
      {(data || []).length === 0 && !loading && (
        <div className="card empty">
          No children linked to your account yet — ask the school admin to add you as a guardian.
        </div>
      )}

      <div className="grid cols-3">
        {(data || []).map((c) => (
          <Link to={`/child/${c.id}`} key={c.id} className="card" style={{ display: 'block' }}>
            <div style={{ fontSize: 32 }}>👦</div>
            <h3 style={{ margin: '8px 0 0' }}>{c.full_name || c.username}</h3>
            <p className="muted" style={{ margin: '4px 0 0' }}>
              View performance &amp; AI summary →
            </p>
          </Link>
        ))}
      </div>
    </div>
  )
}
